# CircuitPython
# Basic functionality test on a Seeeduino XIAO-RP2040 with CircuitPython
#
# Build:
#  $ ./scripts/create_packages.py -c2sC0
#  $ cp build/circuitpython/ILI9225 /media/<user>/CIRCUITPY/lib/
#

import time
from board import MOSI, SCK, D1, D2, D3

from ILI9225.ili9225 import ILI9225
from ILI9225.common import Boards, RGB16BitColor as Color
from ILI9225.default_fonts import Terminal6x8

try:
    from ILI9225.fonts.SansSerif_plain_10 import SansSerif_plain_10
    from ILI9225.fonts.FreeMonoBoldOblique12pt7b import FreeMonoBoldOblique12pt7b
except Exception:
    pass

#           rst, rs, port
tft = ILI9225(D1, D2, 0, D3, MOSI, SCK, board=Boards.RP2040) # ID=1
#tft = ILI9225(D1, D2, 0, D3, MOSI, SCK, board=Boards.SAMD21) # ID=2

print("rst: {}, rs: {}, port: {}, cs: {}, mosi: {}, sck: {}".format(
    tft._rst, tft._rs, tft._spi_port, tft._cs, tft._mosi, tft._sck))

tft.spi_frequency = 80000000

tft.begin()

print("rst: {}, rs: {}, port: {}, cs: {}, mosi: {}, sck: {}".format(
    tft._rst, tft._rs, tft._spi_port, tft._cs, tft._mosi, tft._sck))

tft.draw_rectangle(44, 55, 132, 165, Color.LIGHTGREEN)
tft.fill_triangle(88, 165, 132, 55, 44, 55, Color.YELLOW)
time.sleep(5)
tft.clear(x0=44, y0=55, x1=132, y1=165)
tft.fill_circle(88, 110, 80, color=Color.LIGHTGREEN)
time.sleep(5)
x0 = 8
y0 = 30
x1 = 168
y1 = 190
tft.clear(x0=x0, y0=y0, x1=x1, y1=y1)

# Test orientation
for i in range(4):
    tft.orientation = i
    x0 = tft.max_x // 2
    y0 = tft.max_y // 2
    x1 = tft.max_x // 2 + 80
    y1 = tft.max_y // 2 + 80
    tft.draw_rectangle(x0, y0, x1, y1, Color.BLUEVIOLET)
    time.sleep(2.5)
    print("orientation", i, "x0:", x0, "y0:", y0, "x1:", x1, "y1:", y1)
    tft.clear(x0=x0, y0=y0, x1=x1, y1=y1)

try:
    tft.orientation = 1
    tft.set_font(Terminal6x8)
    msg = "Standard font (Terminal6x8)"
    width, height = tft.get_text_extent(msg)
    print("Text width:", width, "Text height:", height,
          "Max screen width:", tft.max_x)
    x0 = 0
    y0 = tft.max_y / 2
    tft.draw_text(x0, y0, msg, color=Color.MAGENTA, bg_color=Color.YELLOW)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    print("x0:", x0, "y0:", y0, "x1:", x1, "y1:", y1)
    tft.clear(x0=x0, y0=y0, x1=x1, y1=y1)
    time.sleep(3)
except Exception as e:
    print(e)

try:
    tft.orientation = 1
    msg = "GFX Font (SansSerif_plain_10)"
    tft.set_gfx_font(SansSerif_plain_10)
    width, height = tft.get_gfx_text_extent(msg)
    print("GFX font width:", width, "Text height:", height,
          "Max screen width:", tft.max_x)
    x0 = 0
    y0 = tft.max_y / 2
    tft.draw_gfx_text(x0, y0, msg)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    tft.clear(x0=x0, y0=y0-height+1, x1=x1, y1=y1-height+1)
    time.sleep(3)

    msg = "GFX Font BIGGER"
    tft.set_gfx_font(FreeMonoBoldOblique12pt7b)
    width, height = tft.get_gfx_text_extent(msg)
    print("GFX font width:", width, "Text height:", height,
          "Max screen width:", tft.max_x)
    x0 = 0
    y0 = tft.max_y / 2
    tft.draw_gfx_text(x0, y0, msg)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    tft.clear(x0=x0, y0=y0-height+1, x1=x1, y1=y1-height+1)
    time.sleep(3)
except Exception as e:
    print(e)

tft.pin_cleanup()

"""
rst: 32, rs: 33, port: 1, cs: -1, mosi: -1, sck: -1
rst: 32, rs: 33, port: 1, cs: 15, mosi: 13, sck: 14
Text width: 172 Text height: 8 Max screen width: 220
x0: 0 y0: 88.0 x1: 172 y1: 96.0
GFX font width: 176 Text height: 9 Max screen width: 220
GFX font width: 210 Text height: 14 Max screen width: 220
"""
