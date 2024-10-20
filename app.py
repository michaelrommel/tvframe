from machine import Pin
from encoder import Encoder
from button import Button
from touch import PIOCap
from tvledstrip import TVLedStrip
import asyncio
import micropython

# allocate exception buffer
micropython.alloc_emergency_exception_buf(100)

# GPIO definitions, where on the Pico W the individual
# sensors or LEDs are hooked up
pin_clk = 4
pin_dt = 5
pin_sw = 26
pin_led = 27
pin_neo = 28
pin_t_out = 21
pin_t_in = 20


# initialisation tv frame
tvled = TVLedStrip(pin_neo, pin_led)


async def process_rotary(rotary):
    global tvled
    async for value in rotary:
        tvled.setabsolute(value)


async def process_button(button):
    global tvled
    async for press in button:
        if press == Button.SW_SHORT:
            # print("button short")
            tvled.toggle()
        elif press == Button.SW_LONG:
            # print("button long")
            tvled.toggle()
        elif press == PIOCap.TOUCH_SHORT:
            # print("touch short")
            tvled.toggle()
        elif press == PIOCap.TOUCH_LONG:
            # print("touch long")
            tvled.toggle()
        else:
            print(f"unknown button event {press}")


async def main():
    global pin_clk
    global pin_dt
    global pin_sw
    global pin_t_out
    global pin_t_in

    # initialisation of encoder switch
    button = Button(pin_sw)
    asyncio.create_task(process_button(button))

    # initialisation of the PIO state machine 1 for the touch detection
    touch_button = PIOCap(
        0, pin_t_out, pin_t_in, max_count=(10_000), count_freq=10_000_000
    )
    asyncio.create_task(process_button(touch_button))

    # initialisation rotary encoder
    rotary = Encoder(pin_clk, pin_dt, v=10, vmin=0, vmax=20, div=2)
    asyncio.create_task(process_rotary(rotary))

    while True:
        await asyncio.sleep_ms(10_000)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
