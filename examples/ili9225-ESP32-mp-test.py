#
# Basic functionality test on a ESP32 with MicroPython
#

import time

from ILI9225.ili9225 import ILI9225
from ILI9225.common import Boards, RGB16BitColor as Color
from ILI9225.default_fonts import Terminal6x8

try:
    from ILI9225.fonts.Roboto_Mono_Bold_12 import Roboto_Mono_Bold_12
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
tft.clear()
tft.fill_circle(88, 110, 80, color=Color.LIGHTGREEN)
time.sleep(5)
tft.clear()

try:
    tft.orientation = 1
    tft.set_font(Terminal6x8)
    msg = "Std Font (Terminal6x8)"
    print("Text width:", tft.get_text_width(msg))
    x = 0
    y = tft.display_max_y / 2
    tft.draw_text(x, y, msg, color=Color.MAGENTA, bg_color=Color.YELLOW)
    time.sleep(5)
    tft.clear()
except Exception as e:
    print(e)

try:
    tft.orientation = 1
    tft.set_gfx_font(Roboto_Mono_Bold_12)
    msg = "GFX Font (Roboto Mono Bold 12)"
    x = 0
    y = tft.display_max_y / 2
    print("Font extent:", tft.get_gfx_text_extent(x, y, msg))
    tft.draw_gfx_text(x, y, msg)
    time.sleep(5)
    tft.clear()
except Exception as e:
    print(e)

tft.pin_cleanup()
