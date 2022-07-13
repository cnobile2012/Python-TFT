#
# Basic functionality test on a ESP32 with MicroPython
#

import time

from ILI9225.ili9225 import ILI9225
from ILI9225.common import Boards, RGB16BitColor as Color
from ILI9225.default_fonts import Terminal6x8

try:
    from ILI9225.fonts.SansSerif_plain_10 import SansSerif_plain_10
except:
    pass

#          rst, rs, port, cs, mosi, sck
#tft = ILI9225(32, 33, 2, 15, 23, 18, board=Boards.ESP32) # ID=2
tft = ILI9225(32, 33, 1, 15, 13, 14, board=Boards.ESP32) # ID=1

print("rst: {}, rs: {}, port: {}, cs: {}, mosi: {}, sck: {}".format(
    tft._rst, tft._rs, tft._spi_port, tft._cs, tft.mosi, tft.sck))

tft.spi_frequency = 55000000

tft.begin()
tft.draw_rectangle(44, 55, 132, 165, Color.LIGHTGREEN)
tft.fill_triangle(88, 165, 132, 55, 44, 55, Color.YELLOW)
time.sleep(5)
tft.clear(x0=44, y0=55, x1=132, y1=165)
tft.fill_circle(88, 110, 80, color=Color.LIGHTGREEN)
time.sleep(5)
x0 = 88 - 80
y0 = 110 - 80
x1 = 88 + 80
y1 = 110 + 80
tft.clear(x0=x0, y0=y0, x1=x1, y1=y1)

try:
    tft.orientation = 1
    tft.set_font(Terminal6x8)
    msg = "Standard font (Terminal6x8)"
    width, height = tft.get_text_extent(msg)
    print("Text width:", width, "Text height:", height,
          "Max screen width:", tft.display_max_x)
    x0 = 0
    y0 = tft.display_max_y / 2
    tft.draw_text(x0, y0, msg, color=Color.MAGENTA, bg_color=Color.YELLOW)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    print("x0:", x0, "y0:", y0, "x1:", x1, "y1:", y1)
    tft.clear(x0=x0, y0=y0, x1=x1, y1=y1)
except Exception as e:
    print(e)

try:
    tft.orientation = 1
    tft.set_gfx_font(SansSerif_plain_10)
    msg = "GFX Font (SansSerif_plain_10)"
    width, height = tft.get_gfx_text_extent(msg)
    print("GFX font width:", width, "Text height:", height,
          "Max screen width:", tft.display_max_x)
    x0 = 0
    y0 = tft.display_max_y / 2
    tft.draw_gfx_text(x0, y0, msg)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    tft.clear(x0=x0, y0=y0, x1=x1, y1=y1)
except Exception as e:
    print(e)

tft.pin_cleanup()
