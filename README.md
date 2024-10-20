# Room Divider TV Frame

## Motivation

In my apartment I have a pretty open floor plan and almost no doors. There
is a separation wall between the living room and my office space.
Unfortunately my computer monitor is oriented in a way where on a bright
day, the living room windows are almost blindingly bright.

This separation shall provide a little more shielding from the sun and also
hold a TV screen, that should display my photographs but also serve as a
second monitor for the office, if I turn it 180 degrees.

![TV Frame](https://raw.githubusercontent.com/michaelrommel/tvframe/main/assets/tvframe.jpg)

## Electronics

This repo holds some information about the electronics that drive the LED
strip around the TV.

A 110 LED strip needs a dedicated power supply, so a small electronics box
holds the PSU and a mains separating switch in separate compartments from
the low voltage parts. The 5V are on the low voltage part also stabilized
with a large electrolytic capacitor.

![Electronics Box Frame](https://raw.githubusercontent.com/michaelrommel/tvframe/main/assets/box.png)

There are three main input devices that connect to a Raspberry Pi Pico W:

1. a generic encoder KY-040 style with
2. a switch 
3. and a brass plate in the frame that acts as touch switch

In the future the Wifi part of the Pico W will be used to enable a REST
interface, mainly for adjusting the color temperature and provide different
scene settings for the showcase for the espresso cups and the quote / photo
at the top.

One output device is the WS2812B LED strip, that is level shifted by a
SN74HCT245, complete overkill because I just used one of the 8 gates. The
data pin is additionally protected with a small resistor - I think something
in the 300 Ohm range - to avoid reflections and ringing on the wire to the
first pixel.


## Code

The code makes use of several inspirations from across the web:

- Peter Hinch's excellent micropython resources, e.g. https://github.com/peterhinch/micropython-async.git
- Cristof from the micropython forum in the thread https://forum.micropython.org/viewtopic.php?f=21&t=9833&p=55035#top
- several other modules that I had evaluated, e.g. micropython-rotary, but
  decided agains them, due to code structure around hard IRQs.

For the encoder there are a multitude of samples on the net, a few of which
I tried first. Many of them have in common that they do way too much in an
IRQ's callback, also known as Interrupt Service Routine (ISR). The
micropython documentation is actually pretty good in this area and provide
clear guidance, that many developers blatently ignore and you end up with
errors like `schedule queue full` etc.

Peter's libraries carefully avoid that and the code was pretty much, what I
had in mind. When I started this I did not know all the micropytho
n methods
that are available for such scenarios and Peter's docs and examples gave me
a head start, which functions to study and expereriment with. He also was
very kind and answered a few of my questions really quickly, in exchange
those questions also led to a few little code improvements, so win-win...

The code instantiates three objects for the encoder, push button and touch
button, each of which act as `async` iterators and for each object there is
one `asyncio` task that fetches state changes as they become available
(yielded by the iterators) and then change the neopixel strip.

In the encoder and button the ISRs are really small:

- in the encoder just the value is incremented/decremented and a
  ThreadSafeFlag set. A separate asyncio task waits on this flag and uses
  an asyncio event to provide the data to the async iterator
- in the pushbutton the value of the button is pushed into a thread safe
  queue and a ThreadSafeFlag set. Here the async task then takes the button
  state out of the queue and pushes it into a simple python list of no
  fixed lengh. This can be done only here, because memory allocations
  inside ISRs are not supported.

The touch button does not use IRQs, it uses the Pico's PIO state machine to
determine the time the wire and touch button needs to charge and if s.b.
touches the brass plate, the time increases drastically due to the changed
capacity. The time is measured constantly in a busy loop every 50ms. When a
button press is detected it is pushed directly info a python list.

Both buttons then make use ov async events to provide the data to the
`async for in` loops in the main app tasks.

## Next steps

To prove the schematics and code, I created the electronics on a few pieces
of perfboard that I had lying around since the 90s.


![TV Frame](https://raw.githubusercontent.com/michaelrommel/tvframe/main/assets/perfboard_front.jpg)
![TV Frame](https://raw.githubusercontent.com/michaelrommel/tvframe/main/assets/perfboard_back.jpg)

Now is the time to make a proper PCB with all the connetors in their right
places and overall dimensions. Some things are better tested out in real
life, not all can be modeled in CAD...

