# -*- coding: utf-8 -*-
"""
ILI9341/ili9341.py

Driver for the ILI9341 chip TFT LCD displays.
"""

import os

from utils.compatibility import Compatibility
from utils.common import (Boards, CommonMethods, TFTException,
                          CompatibilityException, RGB16BitColor as Colors)


class ILI9341(Compatibility, CommonMethods):
    """
    Main ILI9341 class.
    """
    try:
        DEBUG = eval(os.getenv('TFT_DEBUG', default='False'))
        TESTING = eval(os.getenv('TFT_TESTING', default='False'))
    except AttributeError: # pragma: no cover
        # MicroPython and CircuitPython will raise AttributeError.
        DEBUG = False
        TESTING = False

    LCD_WIDTH        = 240
    LCD_HEIGHT       = 320
    MAX_BRIGHTNESS   = 255   # 0..255

    CMD_NOP          = 0x00 # NOOP
    CMD_SWRESET      = 0x01 # Software Reset
    CMD_RDDID        = 0x04 # Read Display Identification Information
    CMD_RDDST        = 0x09 # Read Display Status
    CMD_RDMODE       = 0x0A # Read Display Power Mode
    CMD_RDMADCTL     = 0x0B # Read Display MADCTL
    CMD_RDPIXFMT     = 0x0C # Read Display Pixel Format
    CMD_RDIMGFMT     = 0x0D # Read Display Image Format
    CMD_RDSIGFMT     = 0x0E # Read Display Signal Mode
    CMD_RDSELFDIAG   = 0x0F # Read Display Self-Diagnostic Result
    CMD_SLPIN        = 0x10 # Enter Sleep Mode
    CMD_SLPOUT       = 0x11 # Exit Sleep Mode (Sleep Out)
    CMD_PTLON        = 0x12 # Partial Mode ON
    CMD_NORON        = 0x13 # Partial Mode OFF (Normal Mode ON)
    CMD_INVOFF       = 0x20 # Display Inversion OFF
    CMD_INVON        = 0x21 # Display Inversion ON
    CMD_GAMMASET     = 0x26 # Gamma Set
    CMD_DISPOFF      = 0x28 # Display OFF
    CMD_DISPON       = 0x29 # Display ON
    CMD_CASET        = 0x2A # Column Address Set
    CMD_RWSET        = 0x2B # Row Address Set (Page Address)
    CMD_WRRAM        = 0x2C # Memory Write
    CMD_COLSET       = 0x2D # Color Set
    CMD_RDRAM        = 0x2E # Memory Read
    CMD_PTLAR        = 0x30 # Partial Area
    CMD_VRSCRL       = 0x33 # Vertical Scrolling Definition
    CMD_TRLNOFF      = 0x34 # Tearing Effect Line OFF
    CMD_TRLNON       = 0x35 # Tearing Effect Line ON
    CMD_MADCTL       = 0x36 # Memory Access Control
    CMD_VRSCRLST     = 0x37 # Vertical Scrolling Start Address
    CMD_IDLEOFF      = 0x38 # Idle Mode OFF
    CMD_IDLEON       = 0x39 # Idle Mode ON
    CMD_PIXFMT       = 0x3A # COLMOD: Pixel Format Set
    CMD_WTMEMCONT    = 0x3C # Write Memory Continue
    CMD_RDMEMCONT    = 0x3E # Read Memory Continue
    CMD_SETSCANLN    = 0x44 # Set Tear Scanline
    CMD_GETSCANLN    = 0x45 # Get Scanline
    CMD_WRDSPBRT     = 0x51 # Write Display Brightness
    CMD_RDDSPBRT     = 0x52 # Read Display Brightness
    CMD_WRCTRLDSP    = 0x53 # Write CTRL Display
    CMD_RDCTRLDSP    = 0x54 # Read CTRL Display
    CMD_WRBRTCTL     = 0x55 # Write Content Adaptive Brightness Control
    CMD_RDBRTCTL     = 0x56 # Read Content Adaptive Brightness Control
    CMD_WRCABCMINBRT = 0x5E # Write CABC Minimum Brightness
    CMD_RDCABCMINBRT = 0x5F # Read CABC Minimum Brightness
    CMD_DSCLVL2      = 0xB0 # Description of Level 2 Command
    CMD_FRMCTR1      = 0xB1 # Frame Rate Control (In Normal Mode/Full Colors)
    CMD_FRMCTR2      = 0xB2 # Frame Rate Control (In Idle Mode/8 colors)
    CMD_FRMCTR3      = 0xB3 # Frame Rate control (In Partial Mode/Full Colors)
    CMD_INVCTR       = 0xB4 # Display Inversion Control
    CMD_BLKPRCHCTL   = 0xB5 # Blanking Porch Control
    CMD_DFUNCTR      = 0xB6 # Display Function Control
    CMD_SETENTYMD    = 0xB7 # Entry Mode Set
    CMD_BCKLITCTL1   = 0xB8 # Backlight Control 1
    CMD_BCKLITCTL2   = 0xB9 # Backlight Control 2
    CMD_BCKLITCTL3   = 0xBA # Backlight Control 3
    CMD_BCKLITCTL4   = 0xBB # Backlight Control 4
    CMD_BCKLITCTL5   = 0xBC # Backlight Control 5
    CMD_BCKLITCTL7   = 0xBE # Backlight Control 7
    CMD_BCKLITCTL8   = 0xBF # Backlight Control 8
    CMD_PWCTR1       = 0xC0 # Power Control 1
    CMD_PWCTR2       = 0xC1 # Power Control 2
    CMD_VMCTR1       = 0xC5 # VCOM Control 1
    CMD_VMCTR2       = 0xC7 # VCOM Control 2
    CMD_PWCTLA       = 0xCB # Power Control A
    CMD_PWCTLB       = 0xCF # Power Control B
    CMD_WRNVMEM      = 0xD0 # NV Memory Write
    CMD_NVMEMPRTKEY  = 0xD1 # NV Memory Protection Key
    CMD_RDNVMEM      = 0xD2 # NV Memory Status Read
    CMD_RDID4        = 0xD3 # Read ID4
    CMD_RDID1        = 0xDA # Read ID1
    CMD_RDID2        = 0xDB # Read ID2
    CMD_RDID3        = 0xDC # Read ID3
    CMD_GMCTRP       = 0xE0 # Positive Gamma Correction
    CMD_GMCTRN       = 0xE1 # Negative Gamma Correction
    CMD_GMCTL1       = 0xE2 # Digital Gamma Control 1
    CMD_GMCTL2       = 0xE3 # Digital Gamma Control 2
    CMD_DRTMCTLA     = 0xE8 # Driver timing control A
    #CMD_DRTMCTLA     = 0xE9 # Driver timing control A ??? It's in the docs
    CMD_DRTMCTLB     = 0xEA # Driver timing control B
    CMD_PWONSEQCTL   = 0xED # Power on sequence control
    CMD_EN3GAMMA     = 0xF2 # Enable 3G
    CMD_IFACECTL     = 0xF6 # Interface Control
    CMD_PUMPRATIOCTL = 0xF7 # Pump ratio control
    CMD_UNKNOWN      = 0xEF # This is an undocumented command but must be sent


    def __init__(self, rst, rs, spi_port, cs=-1, mosi=-1, sck=-1, led=-1,
                 board=None, *, brightness=MAX_BRIGHTNESS, rpi_mode=None):
        """
        Initialize the ILI9225 class.

        :param rst: The RST (reset) pin on the display. (RTD on some devices.)
        :type rst: int
        :param rs: The RS (data/command or DC) pin on the display. 0: command,
                   1: data
        :type rs: int
        :param spi_port: The SPI port to use on the board.
        :type spi_port: int
        :param cs: The CS (chip select) pin on the MCU.
        :type cs: int
        :param mosi: The mosi GPIO number on the MCU.
        :type mosi: int
        :param sck: The SCK GPIO number on the MCU.
        :type sck: int
        :param led: The LED pin on the display.
        :type led: int
        :param brightness: Set the brightness from 0..255 (default=255).
        :type brightness: int
        :param board: The board this will run on. e.g. Boards.ESP32
        :type board: int
        :param rpi_mode: Only applies to the Raspberry Pi and Computer boards.
                         Default GPIO.BCM
        :type rpi_mode: int
        :raises CompatibilityException: If the board is unsupported or the
                                        moso or sck pins are not set on some
                                        boards.
        """
        Compatibility.__init__(self, rpi_mode=rpi_mode)
        CommonMethods.__init__(self)
        self._rst = rst
        self._rs = rs # DC on some boards
        self._spi_port = spi_port
        self._cs = cs
        self._sck = sck
        self._mosi = mosi
        self._miso = -1
        self._led = led
        self.brightness = brightness # Default it maximum brightness.
        self._bl_state = True
        self._max_x = 0
        self._max_y = 0
        self._current_font = None
        self._cfont = CurrentFont()
        self._gfx_font = None
        self.set_board(board)

    def begin(self):
        # Setup MCU specific pins
        self._spi_port_device()

        # Setup reset pin.
        self.pin_mode(self._rst, self.OUTPUT)
        self.digital_write(self._rst, self.LOW)

        # Set up backlight pin, turn off initially.
        if self._led >= 0:
            self.pin_mode(self._led, self.OUTPUT)
            self.setup_pwm(self._led, self.MAX_BRIGHTNESS)
            self.set_backlight(False)

        # Control pins
        self.pin_mode(self._rs, self.OUTPUT)
        self.digital_write(self._rs, self.LOW)
        self.pin_mode(self._cs, self.OUTPUT)
        self.digital_write(self._cs, self.HIGH)

        # Pull the reset pin high to release the reset.
        self.digital_write(self._rst, self.HIGH)
        self.delay(1)
        # Pull the reset pin low to reset the ILI9225.
        self.digital_write(self._rst, self.LOW)
        self.delay(10)
        # Pull the reset pin high to release the reset.
        self.digital_write(self._rst, self.HIGH)
        self.delay(50)

        if self.DEBUG: # pragma: no cover
            print("begin: Finished setting up pins.")

        # Power-on sequence
        self._start_write()
        self.spi_close_override = True
        self._write_register(self.CMD_UNKNOWN, bytearray((0x03, 0x80, 0x02)))
        self._write_register(self.CMD_PWCTLB, bytearray((0x00, 0xC1, 0x30)))
        self._write_register(self.CMD_PWONSEQCTL, bytearray(
            (0x64, 0x03, 0x12, 0x81)))
        self._write_register(self.CMD_DRTMCTLA, bytearray((0x85, 0x00, 0x78)))
        self._write_register(self.CMD_PWCTLA, bytearray(
            (0x39, 0x2C, 0x00, 0x34, 0x02)))
        self._write_register(self.CMD_PUMPRATIOCTL, bytearray((0x20,)))
        self._write_register(self.CMD_DRTMCTLB, bytearray((0x00, 0x00)))
        self._write_register(self.CMD_PWCTR1, bytearray((0x23,)))
        self._write_register(self.CMD_PWCTR2, bytearray((0x10,)))
        self._write_register(self.CMD_VMCTR1, bytearray((0x3e, 0x28)))
        self._write_register(self.CMD_VMCTR2, bytearray((0x86,)))
        self._write_register(self.CMD_MADCTL, bytearray((0x48,)))
        self._write_register(self.CMD_PIXFMT, bytearray((0x55,)))
        self._write_register(self.CMD_FRMCTR1, bytearray((0x00, 0x18)))
        self._write_register(self.CMD_DFUNCTR, bytearray((0x08, 0x82,0x27 )))
        self._write_register(self.CMD_EN3GAMMA, bytearray((0x00,)))
        self._write_register(self.CMD_GAMMASET, bytearray((0x01,)))
        self._write_register(self.CMD_GMCTRP, bytearray(
            (0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1,
             0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00)))
        self._write_register(self.CMD_GMCTRN, bytearray(
            (0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1,
             0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F)))
        self._write_command(self.CMD_SLPOUT)
        self.delay(120)
        self._write_command(self.CMD_DISPON)

        if self.DEBUG: # pragma: no cover
            print("begin: Finished power-on sequence.")

        # Turn on backlight
        self.set_backlight(True)
        self.orientation = 0

        if self.DEBUG: # pragma: no cover
            print("begin: Finished turning on backlight.")

        self.clear()
        self.spi_close_override = False
        self._end_write(reuse=False)

        if self.DEBUG: # pragma: no cover
            print("begin: Finished initialize background color.")

    def set_display(self, flag):
        """
        Set the display on or off.

        :param flag: True = display on and False = display off.
        :type flag: bool
        """
        self._start_write()

        if flag:
            self._write_command(self.CMD_DISPON)
        else:
            self._write_command(self.CMD_DISPOFF)

        self._end_write(reuse=False)
        self.delay(200)

    def draw_pixel_alt(self, pixels):
        """
        Draw a pixel.

        :param pixels: A list of tuples: [(x, y, color),...].
        :type pixels: list
        """
        self._start_write()

        # CMD_CASET (SC[15:8], (SC[7:0], EC[15:8], EC[7:0])
        # CMD_RWSET (SC[15:8], (SC[7:0], EC[15:8], EC[7:0])
        # CMD_RAMWR (D1[17:0], D2[17:0] ... Dn[17:0])

        for x, y, color in pixels:
            if not ((x >= self._max_x) or (y >= self._max_y)):
                x, y = self._orient_coordinates(x, y )
                ## self._write_register(self.CMD_RAM_ADDR_SET1, x)
                ## self._write_register(self.CMD_RAM_ADDR_SET2, y)
                array = bytearray((color >> 8, color & 0xFF))
                ## self._write_register(self.CMD_GRAM_DATA_REG, array)

        self._end_write(reuse=False)

    def _set_window(self, x0, y0, x1, y1): #, mode=MODE_TOP_DOWN_L2R): # 7
        """
        Set the window that will be drawn using the current orientation.

        :param x0: Start x coordinate.
        :type x0: int
        :param y0: Start y continent.
        :type y0: int
        :param x1: End x Continent.
        :type x1: int
        :param y1: End y Continent.
        :type y1: int
        :param mode: The orientation mode.
        :type mode: int
        :raises TFTException: If the orientation is out of range.
        """
        # Clip to TFT-Dimensions
        x0 = min(x0, self._max_x - 1)
        x1 = min(x1, self._max_x - 1)
        y0 = min(y0, self._max_y - 1)
        y1 = min(y1, self._max_y - 1)
        x0, y0 = self._orient_coordinates(x0, y0)
        x1, y1 = self._orient_coordinates(x1, y1)

        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0

        self._start_write()
        self.command(CMD_CASET)  # Column addr set
        self.data(x0 >> 8)
        self.data(x0)            # XSTART
        self.data(x1 >> 8)
        self.data(x1)            # XEND
        self.command(CMD_PASET)  # Row addr set
        self.data(y0 >> 8)
        self.data(y0)            # YSTART
        self.data(y1 >> 8)
        self.data(y1)            # YEND
        self.command(CMD_RAMWR)  # write to RAM
        self._end_write(reuse=False)

    def _reset_window(self):
        self._set_window(0, 0, self.LCD_WIDTH-1, self.LCD_HEIGHT-1)

    def __repr__(self):
        return "<{} object using the {} platform>".format(
            self.__class__.__name__, self.PLATFORM)
