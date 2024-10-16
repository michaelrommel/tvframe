from machine import Pin, PWM
from neopixel import NeoPixel


class PowerLED:
    FREQ = 1000
    FULL = 60 * FREQ
    SLEEP = 6 * FREQ
    OFF = 0

    def __init__(self, led):
        self.led = PWM(Pin(led, Pin.OUT))
        self.led.freq(1000)
        self.dim(PowerLED.FULL)

    def dim(self, value):
        self.led.duty_u16(value)


class TVLedStrip:
    UP = 1
    DOWN = 2

    def __init__(self, neo, led):
        # how many brightness percent to in-/decrease per turn
        self.steps = 5
        # how long is the strip around the tv frame
        self.pixelcount = 110
        # the initial brightness and holder for current value
        self.brightness = 50
        # the max brightness level
        self.brightness_max = 100
        # if the strip is currently on
        self.is_on = True
        # the maximum values for each RGB channel, corresponding
        # to a somewhat warm white setting
        self.max = (255, 140, 120)

        # initialize the strip
        self.neo_pin = Pin(neo, Pin.OUT)
        self.neo = NeoPixel(self.neo_pin, self.pixelcount)
        self.dim(self.brightness)

        # initialize the power led
        self.led = PowerLED(led)

    def get_rgb_percent(self, brightness):
        new = [0, 0, 0]
        for i in range(3):
            new[i] = int(self.max[i] * brightness / 100)
        return new

    def dim(self, value):
        self.neo.fill(self.get_rgb_percent(value))
        self.neo.write()

    def toggle(self):
        # if the last brightness value is zero, there is no sense in toggling
        # the user has to turn the knob to switch the light on
        if self.brightness == 0 and not self.is_on:
            return
        self.is_on = not self.is_on
        if self.is_on:
            self.dim(self.brightness)
            self.led.dim(PowerLED.FULL)
        else:
            self.dim(0)
            self.led.dim(PowerLED.SLEEP)

    def setabsolute(self, value):
        # this is in absolute encoder ranges
        self.brightness = min(100, max(0, value * self.steps))
        # turn it on, if the brightness increases and it was off
        if not self.is_on and value > 0:
            self.toggle()
        # if brightness gets turned to zero toggling will also
        # dim the power LED
        if self.is_on and value == 0:
            self.toggle()
        else:
            self.dim(self.brightness)

    def step(self, direction, count):
        # this would be in relarive steps
        if not self.is_on:
            self.toggle()
            if count > 1:
                count -= 1
            else:
                return
        if direction == TVLedStrip.UP:
            self.brightness += self.steps * count
        elif direction == TVLedStrip.DOWN:
            self.brightness -= self.steps * count
        self.brightness = min(100, max(0, self.brightness))
        self.dim(self.brightness)
