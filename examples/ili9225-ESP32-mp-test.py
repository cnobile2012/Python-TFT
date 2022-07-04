#
# Basic functionality test on a ESP32 with MicroPython
#

import time
#import gc
#import micropython

from ILI9225.ili9225 import ILI9225
from ILI9225.common import Boards, RGB16BitColor as Color

try:
    from ILI9225.fonts.Roboto_Mono_Bold_12 import Roboto_Mono_Bold_12
    from ILI9225.fonts.Roboto_Mono_Bold_14 import Roboto_Mono_Bold_14
except:
    pass

#micropython.mem_info()
#gc.mem_free()
#gc.collect()

"""
from machine import Pin, SPI, PWM, reset
kwargs = {'baudrate': 10000000, 'polarity': 0, 'phase': 0, 'bits': 8,
          'firstbit': SPI.MSB, 'sck': Pin(12), 'mosi': Pin(15)}
spi = SPI(1, **kwargs)
"""

#          rst, rs, port, cs, mosi, sck
#tft = ILI9225(32, 33, 2, 15, 23, 18, board=Boards.ESP32) # ID=2
tft = ILI9225(32, 33, 1, 15, 13, 14, board=Boards.ESP32) # ID=1

print("rst: {}, rs: {}, port: {}, cs: {}, mosi: {}, sck: {}".format(
    tft._rst, tft._rs, tft._spi_port, tft._cs, tft.mosi, tft.sck))

tft.spi_frequency = 20000000

tft.pin_mode(tft._rst, tft.OUTPUT)
tft.digital_write(tft._rst, tft.LOW)
tft.pin_mode(tft._rs, tft.OUTPUT)
tft.digital_write(tft._rs, tft.LOW)
tft.pin_mode(tft._cs, tft.OUTPUT)
tft.digital_write(tft._cs, tft.HIGH)

tft.digital_write(tft._rst, tft.HIGH)
#tft.delay(1)
tft.digital_write(tft._rst, tft.LOW)
#tft.delay(10)
tft.digital_write(tft._rst, tft.HIGH)
#tft.delay(50)

tft._start_write()
tft.spi_close_override = True
tft._write_register(tft.CMD_POWER_CTRL2, 0x0018)
tft._write_register(tft.CMD_POWER_CTRL3, 0x6121)
tft._write_register(tft.CMD_POWER_CTRL4, 0x006F)
tft._write_register(tft.CMD_POWER_CTRL5, 0x495F)
tft._write_register(tft.CMD_POWER_CTRL1, 0x0800)
#tft.delay(10)
tft._write_register(tft.CMD_POWER_CTRL2, 0x103B)
#tft.delay(50)

tft._write_register(tft.CMD_DRIVER_OUTPUT_CTRL, 0x011C)
tft._write_register(tft.CMD_LCD_AC_DRIVING_CTRL, 0x0100)
tft._write_register(tft.CMD_ENTRY_MODE, 0x1038)
tft._write_register(tft.CMD_DISP_CTRL1, 0x0000)
tft._write_register(tft.CMD_BLANK_PERIOD_CTRL1, 0x0808)
tft._write_register(tft.CMD_FRAME_CYCLE_CTRL, 0x1100)
tft._write_register(tft.CMD_INTERFACE_CTRL, 0x0000)
tft._write_register(tft.CMD_OSC_CTRL, 0x0D01)
tft._write_register(tft.CMD_VCI_RECYCLING, 0x0020)
tft._write_register(tft.CMD_RAM_ADDR_SET1, 0x0000)
tft._write_register(tft.CMD_RAM_ADDR_SET2, 0x0000)

tft._write_register(tft.CMD_GATE_SCAN_CTRL, 0x0000)
tft._write_register(tft.CMD_VERTICAL_SCROLL_CTRL1, 0x00DB)
tft._write_register(tft.CMD_VERTICAL_SCROLL_CTRL2, 0x0000)
tft._write_register(tft.CMD_VERTICAL_SCROLL_CTRL3, 0x0000)
tft._write_register(tft.CMD_PARTIAL_DRIVING_POS1, 0x00DB)
tft._write_register(tft.CMD_PARTIAL_DRIVING_POS2, 0x0000)
tft._write_register(tft.CMD_HORIZONTAL_WINDOW_ADDR1, 0x00AF)
tft._write_register(tft.CMD_HORIZONTAL_WINDOW_ADDR2, 0x0000)
tft._write_register(tft.CMD_VERTICAL_WINDOW_ADDR1, 0x00DB)
tft._write_register(tft.CMD_VERTICAL_WINDOW_ADDR2, 0x0000)

tft._write_register(tft.CMD_GAMMA_CTRL1, 0x0000)
tft._write_register(tft.CMD_GAMMA_CTRL2, 0x060B)
tft._write_register(tft.CMD_GAMMA_CTRL3, 0x0C0A)
tft._write_register(tft.CMD_GAMMA_CTRL4, 0x0105)
tft._write_register(tft.CMD_GAMMA_CTRL5, 0x0A0C)
tft._write_register(tft.CMD_GAMMA_CTRL6, 0x0B06)
tft._write_register(tft.CMD_GAMMA_CTRL7, 0x0004)
tft._write_register(tft.CMD_GAMMA_CTRL8, 0x0501)
tft._write_register(tft.CMD_GAMMA_CTRL9, 0x0E00)
tft._write_register(tft.CMD_GAMMA_CTRL10, 0x000E)

tft._write_register(tft.CMD_DISP_CTRL1, 0x0012)
#tft.delay(50)
tft._write_register(tft.CMD_DISP_CTRL1, 0x1017)

tft.set_backlight(True)
tft.orientation = 0
#tft.clear()

#tft.fill_rectangle(0, 0, tft._max_x - 1, tft._max_y - 1, Color.BLACK)

tft.spi_close_override = True
tft._start_write()
x0, y0 = 0, 0
x1, y1 = tft._max_x - 1, tft._max_y - 1
tft._set_window(x0, y0, x1, y1)

for t in reversed(range(1, round((y1 - y0 + 1) * (x1 - x0 + 1)) + 1)):
    tft._write_data(Color.BLACK)

tft._reset_window()
tft.spi_close_override = False

#tft.begin()
#tft.draw_rectangle(44, 55, 132, 165, Color.LIGHTGREEN)
#tft.fill_triangle(88, 165, 132, 55, 44, 55, Color.YELLOW)
#time.sleep(5)
#tft.clear()
#tft.fill_circle(88, 110, 80, color=Colors.LIGHTGREEN)
time.sleep(5)
tft.clear()

#try:
#    tft.set_gfx_font(Roboto_Mono_Bold_14)
#    x = tft.display_max_x / 2
#    y = tft.display_max_y / 2
#    tft.draw_gfx_text(x, y, 'ABC')
#    time.sleep(5)
#    tft.clear()
#except:
#    pass

tft.pin_cleanup()
