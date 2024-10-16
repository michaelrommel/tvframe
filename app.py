from machine import Pin
from encoder import Encoder
from button import Button
from tvledstrip import TVLedStrip
from time import ticks_ms, ticks_diff
import asyncio

# GPIO definitions, where on the Pico W the individual
# sensors or LEDs are hooked up
pin_clk = 4
pin_dt = 5
pin_sw = 26
pin_led = 27
pin_neo = 28

# button press parameters
last_press = ticks_ms()
last_release = ticks_ms()
# values in ms for debouncing and long press detection
debounce = 100
long_press = 1000

# initialisation tv frame
tvled = TVLedStrip(pin_neo, pin_led)


def rotary_callback(value, delta):
    global tvled
    tvled.setabsolute(value)


def switch_callback(change):
    global last_press
    global last_release
    global debounce
    global tvled

    if change == Button.SW_PRESS:
        now = ticks_ms()
        diff = ticks_diff(now, last_press)
        last_press = now
        if diff < debounce:
            print("bouncing ignored")
            return
    elif change == Button.SW_RELEASE:
        now = ticks_ms()
        diff = ticks_diff(now, last_release)
        last_release = now
        if diff < debounce:
            print("bouncing ignored")
            return
        duration = ticks_diff(last_release, last_press)
        # distinction not used yet, need to see what a suitable
        # function might be
        if duration > long_press:
            print(f"long press: {duration}")
        else:
            print(f"short press: {duration}")
        tvled.toggle()


# initialisation of encoder switch
button = Button(pin_sw)
button.add_handler(switch_callback)

# set up the pins here, the encoder expects Pins not pin numbers
pin_x = Pin(pin_clk, Pin.IN)
pin_y = Pin(pin_dt, Pin.IN)


async def main():
    global pin_x
    global pin_y

    # initialisation rotary encoder
    rotary = Encoder(
        pin_x, pin_y, v=10, vmin=0, vmax=20, div=2, callback=rotary_callback
    )

    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
