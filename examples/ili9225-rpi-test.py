#
# Basic functionality test on a Raspberry Pi
#

import time

from ILI9225 import ILI9225, Boards, RGB16BitColor as Color

try:
    from ILI9225.fonts.Roboto_Mono_Bold_12 import Roboto_Mono_Bold_12
    from ILI9225.fonts.Roboto_Mono_Bold_14 import Roboto_Mono_Bold_14
except:
    pass

#          rst, rs, port, cs
tft = ILI9225(17, 27, 0, 8, led=22, board=Boards.RASPI)
tft.begin()
tft.draw_rectangle(44, 55, 132, 165, Color.LIGHTGREEN)
tft.fill_triangle(88, 165, 132, 55, 44, 55, Color.YELLOW)
time.sleep(5)
tft.clear()
tft.fill_circle(88, 110, 80, color=Colors.LIGHTGREEN)
time.sleep(5)
tft.clear()

try:
    tft.set_gfx_font(Roboto_Mono_Bold_14)
    x = tft.display_max_x / 2
    y = tft.display_max_y / 2
    tft.draw_gfx_text(x, y, 'ABC')
    time.sleep(5)
except:
    pass

tft.pin_cleanup()
