from machine import Pin, PWM
from neopixel import NeoPixel
from rotary import Rotary
from time import ticks_ms, ticks_diff

def get_rgb_percent(brightness):
    red = int(255 * brightness / 100)
    green = int(140 * brightness / 100)
    blue = int(120 * brightness / 100)
    return (red,green,blue)

print("Initialising")

pixelcount = 110
brightness = 50
brightness_max = 100
lighton = True
last_tick = ticks_ms()
debounce = 100

# GPIO definitions
pin_clk = 4
pin_dt = 5
pin_sw = 26
pin_led = 27
pin_neo = 28

# Initialiserung Rotary Encoder
rotary = Rotary(pin_dt, pin_clk, pin_sw)
value = int(60000)

# Neopixel Strip
neopin = Pin(pin_neo, Pin.OUT)
np = NeoPixel(neopin, pixelcount)
np.fill(get_rgb_percent(brightness))
np.write()

# Power LED
led = PWM(Pin(pin_led, Pin.OUT))
led.freq(1000)
led.duty_u16(value)

def rotary_changed(change):
    global np
    global brightness
    global brightness_max
    global lighton
    global value
    global last_tick
    global debounce
    if change == Rotary.ROT_CW:
        lighton = True
        brightness += 5
        if brightness >= brightness_max:
            brightness = brightness_max
        np.fill(get_rgb_percent(brightness))
        value = int(60000)
        print('clockwise (', brightness, ')')
    elif change == Rotary.ROT_CCW:
        lighton = True
        brightness -= 5
        if brightness < 0:
            brightness = 0
        np.fill(get_rgb_percent(brightness))
        value = int(60000)
        print('counterclockwise (', brightness, ')')
    elif change == Rotary.SW_PRESS:
        now = ticks_ms()
        diff = ticks_diff(now, last_tick)
        last_tick = now
        if diff < debounce:
            print("bouncing ignored")
            return
        lighton = not lighton
        if lighton:
            np.fill(get_rgb_percent(brightness))
            value = int(60000)
        else:
            np.fill((0,0,0))
            value = int(6000)
    led.duty_u16(value)
    np.write()

rotary.add_handler(rotary_changed)

print("End of app.py")
