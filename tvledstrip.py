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
        self.is_on = not self.is_on
        if self.is_on:
            self.dim(self.brightness)
            self.led.dim(PowerLED.FULL)
        else:
            self.dim(0)
            self.led.dim(PowerLED.SLEEP)

    def step(self, direction):
        if not self.is_on:
            self.toggle()
            return
        else:
            if direction == TVLedStrip.UP:
                self.brightness += self.steps
                if self.brightness >= self.brightness_max:
                    self.brightness = self.brightness_max
            elif direction == TVLedStrip.DOWN:
                self.brightness -= self.steps
                if self.brightness < 0:
                    self.brightness = 0
            self.dim(self.brightness)
