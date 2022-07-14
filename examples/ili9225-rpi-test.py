#!/usr/bin/env python3
#
# Basic functionality test on a Raspberry Pi
#

import os
import sys
import time

if len(sys.argv) > 1:
    build = sys.argv[1]
else:
    build = ''

ROOT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', build))
sys.path.append(ROOT_PATH)

from ILI9225 import ILI9225, Boards, Terminal6x8, RGB16BitColor as Color

try:
    from ILI9225.fonts.SansSerif_plain_10 import SansSerif_plain_10
    from ILI9225.fonts.FreeMonoBoldOblique12pt7b import (
        FreeMonoBoldOblique12pt7b,)
except:
    try:
        from fonts.SansSerif_plain_10 import SansSerif_plain_10
        from fonts.FreeMonoBoldOblique12pt7b import FreeMonoBoldOblique12pt7b
    except:
        pass

#          rst, rs, port, cs
tft = ILI9225(17, 27, 0, 8, board=Boards.RASPI)

#tft.spi_frequency = 100000000

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
    msg = "Standard Font (Terminal6x8)"
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
    msg = "GFX Font (SansSerif_plain_10)"
    tft.set_gfx_font(SansSerif_plain_10)
    width, height = tft.get_gfx_text_extent(msg)
    print("GFX font width:", width, "Text height:", height,
          "Max screen width:", tft.display_max_x)
    x0 = 0
    y0 = tft.display_max_y / 2
    tft.draw_gfx_text(x0, y0, msg)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    tft.clear(x0=x0, y0=y0-8, x1=x1, y1=y1-8)

    msg = "GFX Font BIGGER"
    tft.set_gfx_font(FreeMonoBoldOblique12pt7b)
    width, height = tft.get_gfx_text_extent(msg)
    print("GFX font width:", width, "Text height:", height,
          "Max screen width:", tft.display_max_x)
    x0 = 0
    y0 = tft.display_max_y / 2 - 15
    tft.draw_gfx_text(x0, y0, msg)
    time.sleep(5)
    x1 = x0 + width
    y1 = y0 + height
    tft.clear(x0=x0, y0=y0-13, x1=x1, y1=y1-13)
except Exception as e:
    print(e)

tft.pin_cleanup()
