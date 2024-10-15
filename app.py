from rotary import Rotary
from tvledstrip import TVLedStrip
from time import ticks_ms, ticks_diff

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

# initialisation rotary encoder
rotary = Rotary(pin_dt, pin_clk, pin_sw)

# initialisation tv frame
tvled = TVLedStrip(pin_neo, pin_led)

def rotary_change(change):
    global last_press
    global last_release
    global debounce
    global tvled

    if change == Rotary.ROT_CW:
        tvled.step(TVLedStrip.UP)
    elif change == Rotary.ROT_CCW:
        tvled.step(TVLedStrip.DOWN)
    elif change == Rotary.SW_PRESS:
        now = ticks_ms()
        diff = ticks_diff(now, last_press)
        last_press = now
        if diff < debounce:
            print("bouncing ignored")
            return
    elif change == Rotary.SW_RELEASE:
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
            print(f"Short press: {duration}")
        tvled.toggle()

rotary.add_handler(rotary_change)
