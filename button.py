from machine import Pin
import micropython


class Button:
    SW_PRESS = 1
    SW_RELEASE = 2

    def __init__(self, sw):
        self.sw_pin = Pin(sw, Pin.IN, Pin.PULL_UP)
        self.sw_pin.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self.switch_detect,
        )
        self.handlers = []
        self.last_button_status = self.sw_pin.value()

    def switch_detect(self, pin):
        if self.last_button_status == self.sw_pin.value():
            return
        self.last_button_status = self.sw_pin.value()
        if self.sw_pin.value():
            micropython.schedule(self.call_handlers, Button.SW_RELEASE)
        else:
            micropython.schedule(self.call_handlers, Button.SW_PRESS)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def call_handlers(self, type):
        for handler in self.handlers:
            handler(type)

