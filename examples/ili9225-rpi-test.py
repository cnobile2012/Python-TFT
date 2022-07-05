#!/usr/bin/env python3
#
# Basic functionality test on a Raspberry Pi
#

import os
import sys
import time

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_PATH)

from ILI9225 import ILI9225, Boards, RGB16BitColor as Color
from ILI9225.default_fonts import Terminal11x16

try:
    from ILI9225.fonts.Roboto_Mono_Bold_12 import Roboto_Mono_Bold_12
except:
    try:
        from fonts.Roboto_Mono_Bold_12 import Roboto_Mono_Bold_12
    except:
        pass

#          rst, rs, port, cs
tft = ILI9225(17, 27, 0, 8, board=Boards.RASPI)

tft.spi_frequency = 100000000

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
    tft.set_font(Terminal11x16)
    msg = "Std Font (Terminal12x16)"
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
