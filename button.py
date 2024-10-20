from machine import Pin
from threadsafe_queue import ThreadSafeQueue
from time import ticks_ms, ticks_diff
import asyncio


class Button:
    SW_SHORT = 1
    SW_LONG = 2

    def __init__(self, pin_sw):
        # button press parameters
        self.last_press = ticks_ms()
        self.last_release = ticks_ms()
        # values in ms for debouncing and long press detection
        self.debounce = 80
        self.long_press = 750
        self.buffer = []
        self.queue = ThreadSafeQueue(20)
        self._pin = Pin(pin_sw, Pin.IN, Pin.PULL_UP)
        self._pin.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self.sw_isr,
        )
        self.evt = asyncio.Event()
        self.last_button_status = self._pin.value()
        asyncio.create_task(self._run())

    async def _run(self):
        while True:
            sw = await self.queue.get()

            if not sw:
                # button pressed
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
                    Button.SW_LONG if (duration > self.long_press) else Button.SW_SHORT
                )
                self.evt.set()

    def sw_isr(self, pin):
        if (sw := pin.value()) != self.last_button_status:
            self.last_button_status = sw
            try:
                self.queue.put_sync(sw)
            except IndexError:
                pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.evt.wait()
        self.evt.clear()
        return self.buffer.pop(0)
