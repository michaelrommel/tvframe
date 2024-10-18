from machine import Pin
from rp2 import PIO, StateMachine, asm_pio


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
    def __init__(self, sm_id, outPin, inPin, max_count, count_freq):
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

    def getCap(self):
        self._sm.exec("push()")
        # Since the PIO can only decrement, convert it back into +ve
        return self._sm.get()
