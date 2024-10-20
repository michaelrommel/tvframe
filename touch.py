from machine import Pin
from threadsafe_queue import ThreadSafeQueue
from rp2 import PIO, StateMachine, asm_pio
from time import ticks_ms, ticks_diff
import asyncio


@asm_pio(sideset_init=PIO.OUT_LOW)
def cap_prog():
    mov(y, osr).side(1)  # OSR must be preloaded with max
    mov(x, osr).side(1)

    label("test_pin")  # count down y, until inPin is high
    jmp(pin, "is_set")  # does work
    jmp(y_dec, "test_pin")  # tested

    label("is_set")
    mov(isr, y).side(0)  # save result pin low

    label("delayLow")
    nop()
    jmp(x_dec, "delayLow")  # tested


class PIOCap:
    TOUCH_SHORT = 4
    TOUCH_LONG = 8

    def __init__(self, sm_id, outPin, inPin, max_count, count_freq):
        # button press parameters
        self.last_press = ticks_ms()
        self.last_release = ticks_ms()
        # values in ms for debouncing and long press detection
        self.debounce = 80
        self.long_press = 750
        self.buffer = []
        self._sm = StateMachine(
            sm_id,
            cap_prog,
            freq=2 * count_freq,
            sideset_base=Pin(outPin),
            jmp_pin=Pin(inPin, Pin.IN),
        )
        # Use exec() to load max count into ISR
        self._sm.put(max_count)
        self._sm.exec("pull()")
        # self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count
        self.evt = asyncio.Event()
        self.touched = False
        asyncio.create_task(self._run())

    def getCap(self):
        self._sm.exec("push()")
        # Since the PIO can only decrement, convert it back into +ve
        return self._sm.get()

    async def _run(self):
        while True:
            touchState = True if (10_000 - self.getCap()) > 400 else False
            if touchState != self.touched:
                self.touched = touchState

                if self.touched:
                    # button touched
                    now = ticks_ms()
                    diff = ticks_diff(now, self.last_press)
                    self.last_press = now
                    if diff < self.debounce:
                        continue
                else:
                    # button released
                    now = ticks_ms()
                    diff = ticks_diff(now, self.last_release)
                    self.last_release = now
                    if diff < self.debounce:
                        continue
                    duration = ticks_diff(self.last_release, self.last_press)
                    self.buffer.append(
                        PIOCap.TOUCH_LONG
                        if (duration > self.long_press)
                        else PIOCap.TOUCH_SHORT
                    )
                    self.evt.set()
            await asyncio.sleep_ms(50)

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.evt.wait()
        self.evt.clear()
        return self.buffer.pop(0)
