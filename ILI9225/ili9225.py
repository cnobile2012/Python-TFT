# -*- coding: utf-8 -*-
"""
ILI9225/ili9225.py

Driver for the ILI9225 chip TFT LCD displays.
"""

import os

from utils.compatibility import Compatibility
from utils.common import (Boards, TFTException, CompatibilityException,
                          RGB16BitColor as Colors)


class AutoIncMode:
    R2L_BOTTOM_UP = 0
    BOTTOM_UP_R2L = 1
    L2R_BOTTOM_UP = 2
    BOTTOM_UP_L2R = 3
    R2L_TOP_DOWN = 4
    TOP_DOWN_R2L = 5
    L2R_TOP_DOWN = 6
    TOP_DOWN_L2R = 7


class CurrentFont:
    """
    Stores the currently used standard font.
    """

    def __init__(self, font=((), 0, 0, 0, 0, 0, False)):
        self.set_font(font)

    def set_font(self, font):
        """
        Set a standard font.

        .. note::

          Tuple definition: font = Full data object
                            width = 1st byte in full data object
                            height = 2nd byte in full data object
                            offset = 3rd byte in full data object
                            numchars = 4th byte in full data object
                            nbrows = 2nd byte / 8 in full data object
                            mono_sp = Boolean indicating if mono spaced

        :param font: A parsed font object.
        :type font: tuple
        """
        self.font = font[0]
        self.width = font[1]
        self.height = font[2]
        self.offset = font[3]
        self.numchars = font[4]
        # Set number of bytes used by height of font in multiples of 8
        self.nbrows = font[5] + 1 if self.height % 8 else font[5]
        self.mono_sp = font[6]


class GFXGlyph:
    """
    Glyph structure data.
    """

    def __init__(self, glyph):
        self.bitmap_offset = glyph[0] # GFXFont.bitmap
        self.width = glyph[1]         # Bitmap dimensions in pixels
        self.height = glyph[2]
        self.x_advance = glyph[3]     # Distance to advance cursor (x axis)
        self.x_offset = glyph[4]      # Distance from cursor pos to UL corner
        self.y_offset = glyph[5]


class GFXFont:
    """
    Font meta data for the font bitmaps and glyphs.
    """

    def __init__(self, font):
        self.bitmap = font[0]    # Bitmaps
        self.glyph = font[1]     # Glyphs
        self.first = font[2]     # ASCII extents
        self.last = font[3]
        self.y_advance = font[4] # Newline distance (y axis)


class ILI9225(Compatibility):
    """
    Main ILI9225 class.
    """
    try:
        DEBUG = eval(os.getenv('TFT_DEBUG', default='False'))
        TESTING = eval(os.getenv('TFT_TESTING', default='False'))
    except AttributeError: # pragma: no cover
        # MicroPython and CircuitPython will raise AttributeError.
        DEBUG = False
        TESTING = False

    ERROR_MSGS = {
        'STD_FONT': "Please set a standard font before using this method.",
        'GFX_FONT': "Please set a GFX font before using this method.",
        'GFX_BAD_CH': "The character '{}' is not in the current font.",
        'BRD_UNSUP': "Error: The {} board is not supported.",
        'INV_PORT': "Invalid port for the {} board."
        }

    LCD_WIDTH                   = 176
    LCD_HEIGHT                  = 220
    MAX_BRIGHTNESS              = 255   # 0..255

    CMD_DRIVER_OUTPUT_CTRL      = 0x01  # Driver Output Control
    CMD_LCD_AC_DRIVING_CTRL     = 0x02  # LCD AC Driving Control
    CMD_ENTRY_MODE              = 0x03  # Entry Mode
    CMD_DISP_CTRL1              = 0x07  # Display Control 1
    CMD_BLANK_PERIOD_CTRL1      = 0x08  # Blank Period Control
    CMD_FRAME_CYCLE_CTRL        = 0x0B  # Frame Cycle Control
    CMD_INTERFACE_CTRL          = 0x0C  # Interface Control
    CMD_OSC_CTRL                = 0x0F  # Osc Control
    CMD_POWER_CTRL1             = 0x10  # Power Control 1
    CMD_POWER_CTRL2             = 0x11  # Power Control 2
    CMD_POWER_CTRL3             = 0x12  # Power Control 3
    CMD_POWER_CTRL4             = 0x13  # Power Control 4
    CMD_POWER_CTRL5             = 0x14  # Power Control 5
    CMD_VCI_RECYCLING           = 0x15  # VCI Recycling
    CMD_RAM_ADDR_SET1           = 0x20  # Horizontal GRAM Address Set
    CMD_RAM_ADDR_SET2           = 0x21  # Vertical GRAM Address Set
    CMD_GRAM_DATA_REG           = 0x22  # GRAM Data Register
    CMD_GATE_SCAN_CTRL          = 0x30  # Gate Scan Control Register
    CMD_VERTICAL_SCROLL_CTRL1   = 0x31  # Vertical Scroll Control 1 Register
    CMD_VERTICAL_SCROLL_CTRL2   = 0x32  # Vertical Scroll Control 2 Register
    CMD_VERTICAL_SCROLL_CTRL3   = 0x33  # Vertical Scroll Control 3 Register
    CMD_PARTIAL_DRIVING_POS1    = 0x34  # Partial Driving Position 1 Register
    CMD_PARTIAL_DRIVING_POS2    = 0x35  # Partial Driving Position 2 Register
    CMD_HORIZONTAL_WINDOW_ADDR1 = 0x36  # Horizontal Address Start Position
    CMD_HORIZONTAL_WINDOW_ADDR2 = 0x37  # Horizontal Address End Position
    CMD_VERTICAL_WINDOW_ADDR1   = 0x38  # Vertical Address Start Position
    CMD_VERTICAL_WINDOW_ADDR2   = 0x39  # Vertical Address End Position
    CMD_GAMMA_CTRL1             = 0x50  # Gamma Control 1
    CMD_GAMMA_CTRL2             = 0x51  # Gamma Control 2
    CMD_GAMMA_CTRL3             = 0x52  # Gamma Control 3
    CMD_GAMMA_CTRL4             = 0x53  # Gamma Control 4
    CMD_GAMMA_CTRL5             = 0x54  # Gamma Control 5
    CMD_GAMMA_CTRL6             = 0x55  # Gamma Control 6
    CMD_GAMMA_CTRL7             = 0x56  # Gamma Control 7
    CMD_GAMMA_CTRL8             = 0x57  # Gamma Control 8
    CMD_GAMMA_CTRL9             = 0x58  # Gamma Control 9
    CMD_GAMMA_CTRL10            = 0x59  # Gamma Control 10

    # 1: pixel width of 1 font character, 2: pixel height
    _CFONT_HEADER_SIZE = 4

    # Corresponding modes when orientation changes.
    _MODE_TAB = (
        (AutoIncMode.BOTTOM_UP_L2R, AutoIncMode.L2R_BOTTOM_UP,
         AutoIncMode.TOP_DOWN_L2R, AutoIncMode.L2R_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_R2L, AutoIncMode.R2L_BOTTOM_UP,
         AutoIncMode.TOP_DOWN_R2L, AutoIncMode.R2L_TOP_DOWN), # 90??
        (AutoIncMode.L2R_TOP_DOWN, AutoIncMode.TOP_DOWN_L2R,
         AutoIncMode.R2L_TOP_DOWN, AutoIncMode.TOP_DOWN_R2L,
         AutoIncMode.L2R_BOTTOM_UP, AutoIncMode.BOTTOM_UP_L2R,
         AutoIncMode.R2L_BOTTOM_UP, AutoIncMode.BOTTOM_UP_R2L), # 180??
        (AutoIncMode.TOP_DOWN_R2L, AutoIncMode.R2L_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_R2L, AutoIncMode.R2L_BOTTOM_UP,
         AutoIncMode.TOP_DOWN_L2R, AutoIncMode.L2R_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_L2R, AutoIncMode.L2R_BOTTOM_UP) # 270??
        )

    def __init__(self, rst, rs, spi_port, cs=-1, mosi=-1, sck=-1, led=-1,
                 board=None, *, brightness=MAX_BRIGHTNESS, rpi_mode=None):
        """
        Initialize the ILI9225 class.

        :param rst: The RST (reset) pin on the display. (RTD on some devices.)
        :type rst: int
        :param rs: The RS (command/data) pin on the display. 0: command, 1: data
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
        super().__init__(rpi_mode=rpi_mode)
        self._rst = rst
        self._rs = rs
        self._spi_port = spi_port
        self._cs = cs
        self._sck = sck
        self._mosi = mosi
        self._miso = -1
        self._led = led
        self.__brightness = 0
        self.brightness = brightness # Default it maximum brightness.
        self.__orientation = 0
        self._bl_state = True
        self._max_x = 0
        self._max_y = 0
        self.__spi_close_override = False
        self._current_font = None
        self._cfont = CurrentFont()
        self._gfx_font = None
        self.set_board(board)

    @property
    def spi_close_override(self):
        """
        Returns the override state of the SPI interface.

        :return: If the override is active the result is True,
                 if not active it is False.
        :rtype: bool
        """
        return self.__spi_close_override

    @spi_close_override.setter
    def spi_close_override(self, value):
        """
        Sets the override state of the SPI interface.

        :param value: If True the SPI interface close is overridden
                      else if False it is not overridden.
        :type value: bool
        """
        self.__spi_close_override = value

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
        # Set APON,PON,AON,VCI1EN,VC
        self._write_register(self.CMD_POWER_CTRL2, 0x0018)
        # Set BT,DC1,DC2,DC3
        self._write_register(self.CMD_POWER_CTRL3, 0x6121)
        # Set GVDD (007F 0088)
        self._write_register(self.CMD_POWER_CTRL4, 0x006F)
        # Set VCOMH/VCOML voltage
        self._write_register(self.CMD_POWER_CTRL5, 0x495F)
        # Set SAP,DSTB,STB
        self._write_register(self.CMD_POWER_CTRL1, 0x0800)
        self.delay(10)
        # Set APON,PON,AON,VCI1EN,VC
        self._write_register(self.CMD_POWER_CTRL2, 0x103B)
        self.delay(50)

        # Set the display line number and display direction
        self._write_register(self.CMD_DRIVER_OUTPUT_CTRL, 0x011C) # 0x001C
        # Set 1 line inversion
        self._write_register(self.CMD_LCD_AC_DRIVING_CTRL, 0x0100)
        # Set GRAM write direction and BGR=1.
        self._write_register(self.CMD_ENTRY_MODE, 0x1038) # 0x0038
        # Display off
        self._write_register(self.CMD_DISP_CTRL1, 0x0000)
        # Set the back porch and front porch
        self._write_register(self.CMD_BLANK_PERIOD_CTRL1, 0x0808)
        # Set the clocks number per line
        self._write_register(self.CMD_FRAME_CYCLE_CTRL, 0x1100)
        # CPU interface
        self._write_register(self.CMD_INTERFACE_CTRL, 0x0000)
        # 0e01
        self._write_register(self.CMD_OSC_CTRL, 0x0D01)
        # Set VCI recycling
        self._write_register(self.CMD_VCI_RECYCLING, 0x0020)
        # RAM Address
        self._write_register(self.CMD_RAM_ADDR_SET1, 0x0000)
        self._write_register(self.CMD_RAM_ADDR_SET2, 0x0000)

        if self.DEBUG: # pragma: no cover
            print("begin: Finished power-on sequence.")

        # Set GRAM area
        self._write_register(self.CMD_GATE_SCAN_CTRL, 0x0000)
        self._write_register(self.CMD_VERTICAL_SCROLL_CTRL1, 0x00DB)
        self._write_register(self.CMD_VERTICAL_SCROLL_CTRL2, 0x0000)
        self._write_register(self.CMD_VERTICAL_SCROLL_CTRL3, 0x0000)
        self._write_register(self.CMD_PARTIAL_DRIVING_POS1, 0x00DB)
        self._write_register(self.CMD_PARTIAL_DRIVING_POS2, 0x0000)
        self._write_register(self.CMD_HORIZONTAL_WINDOW_ADDR1, 0x00AF)
        self._write_register(self.CMD_HORIZONTAL_WINDOW_ADDR2, 0x0000)
        self._write_register(self.CMD_VERTICAL_WINDOW_ADDR1, 0x00DB)
        self._write_register(self.CMD_VERTICAL_WINDOW_ADDR2, 0x0000)

        if self.DEBUG: # pragma: no cover
            print("begin: Finished set GRAM area.")

        # Adjust GAMMA curve
        self._write_register(self.CMD_GAMMA_CTRL1, 0x0000)
        self._write_register(self.CMD_GAMMA_CTRL2, 0x060B)
        self._write_register(self.CMD_GAMMA_CTRL3, 0x0C0A)
        self._write_register(self.CMD_GAMMA_CTRL4, 0x0105)
        self._write_register(self.CMD_GAMMA_CTRL5, 0x0A0C)
        self._write_register(self.CMD_GAMMA_CTRL6, 0x0B06)
        self._write_register(self.CMD_GAMMA_CTRL7, 0x0004)
        self._write_register(self.CMD_GAMMA_CTRL8, 0x0501)
        self._write_register(self.CMD_GAMMA_CTRL9, 0x0E00)
        self._write_register(self.CMD_GAMMA_CTRL10, 0x000E)

        self._write_register(self.CMD_DISP_CTRL1, 0x0012)
        self.delay(50)
        self._write_register(self.CMD_DISP_CTRL1, 0x1017)

        if self.DEBUG: # pragma: no cover
            print("begin: Finished set GAMMA curve.")

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

    def clear(self, x0=None, y0=None, x1=None, y1=None, color=Colors.BLACK):
        """
        Overwrites the entire display with the color black.

        .. note::

          This method can be used to clear, to the previously set
          background color, a rectilinear area to clear a previous object
          on the display. Circles can be cleared however the area must be
          rectilinear. Any intersecting lines or objects will also be cleared.

        :param x0: Start x coordinate.
        :type x0: int
        :param y0, Start y coordinate.
        :type y0: int
        :param x1: End x coordinate.
        :type x1: int
        :param y1, End y coordinate.
        :type y1: int
        """
        if any([True for v in (x0, y0, x1, y1) if v is None]):
            self.set_display_background(color)
        else:
            self.fill_rectangle(x0, y0, x1, y1, color)

    def set_display_background(self, color):
        """
        Set the background color of the display.

        :param color: The RGB color for the display, default is black.
        :type color: int
        """
        old_orientation = self.orientation
        self.orientation = 0
        self.fill_rectangle(0, 0, self._max_x - 1, self._max_y - 1, color)
        self.orientation = old_orientation
        self.delay(10)

    def set_backlight(self, flag, brightness=MAX_BRIGHTNESS):
        """
        Set the backlight on or off and set the brightness if there
        is an LED pin.

        :param flag: True = backlight on and False = backlight off.
        :type flag: bool
        """
        self._bl_state = flag

        if self._led >= 0:
            self.brightness = brightness
            self.change_duty_cycle(
                self._led, self.brightness if self._bl_state else 0)

    @property
    def brightness(self):
        """
        Get the current brightness.
        """
        return self.__brightness

    @brightness.setter
    def brightness(self, brightness):
        """
        Set a different brightness.

        :param brightness: The brightness value to set (0 .. 255)
        """
        self.__brightness = brightness % (self.MAX_BRIGHTNESS + 1)

    def set_display(self, flag):
        """
        Set the display on or off.

        :param flag: True = display on and False = display off.
        :type flag: bool
        """
        if flag:
            self._start_write()
            self._write_register(0x00ff, 0x0000)
            self._write_register(self.CMD_POWER_CTRL1, 0x0000)
            self.delay(50)
            self._write_register(self.CMD_DISP_CTRL1, 0x1017)
            self._end_write(reuse=False)
            self.delay(200)
        else:
            self._start_write()
            self._write_register(0x00ff, 0x0000)
            self._write_register(self.CMD_DISP_CTRL1, 0x0000)
            self.delay(50)
            self._write_register(self.CMD_POWER_CTRL1, 0x0003)
            self._end_write(reuse=False)
            self.delay(200)

    @property
    def orientation(self):
        """
        Get the orientation.

        :return: Return the current orientation.
        :rtype: int
        """
        return self.__orientation

    @orientation.setter
    def orientation(self, orientation):
        """
        Set the orientation.

        :param orientation: 0=portrait, 1=right rotated landscape,
                            2=reverse portrait, 3=left rotated landscape
        :type orientation: int
        """
        self.__orientation = orientation % 4

        if self.__orientation == 0: # 0=portrait
            self._max_x = self.LCD_WIDTH
            self._max_y = self.LCD_HEIGHT
        elif self.__orientation == 1: # 1=right rotated landscape
            self._max_x = self.LCD_HEIGHT
            self._max_y = self.LCD_WIDTH
        elif self.__orientation == 2: # 2=reverse portrait
            self._max_x = self.LCD_WIDTH
            self._max_y = self.LCD_HEIGHT
        elif self.__orientation == 3: # 3=left rotated landscape
            self._max_x = self.LCD_HEIGHT
            self._max_y = self.LCD_WIDTH

    def _orient_coordinates(self, x, y):
        if self.__orientation == 1:
            y = self._max_y - y - 1
            x, y = y, x
        elif self.__orientation == 2:
            x = self._max_x - x - 1
            y = self._max_y - y - 1
        elif self.__orientation == 3:
            x = self._max_x - x - 1
            x, y = y, x

        # if self.__orientation == 0: We fall through.
        return x, y

    @property
    def display_max_x(self):
        """
        Get the display max x size (based on orientation).

        .. note::

          Either 0..176 or 0..220 depending on orientation.

        :return: Horizontal size of the display in pixels.
        :rtype: int
        """
        return self._max_x

    @property
    def display_max_y(self):
        """
        Get the display max y size (based on orientation).

        .. note::

          Either 0..176 or 0..220 depending on orientation.

        :return: Vertical size of the display in pixels.
        :rtype: int
        """
        return self._max_y

    #
    # Beginning of standard font methods.
    #
    def set_font(self, font, mono_sp=False):
        """
        Set the current font.

        :param font: The name of the font.
        :type font: str
        :param mono_sp: True = Mono spaced, False = Proportional
        :type mono_sp: bool
        """
        #       font, width,   height,  offset,  numchars, height / 8
        args = (font, font[0], font[1], font[2], font[3], font[1] // 8,
                mono_sp)
        self._cfont.set_font(args)

    def get_font(self):
        """
        Get the current font.

        :return: The current font.
        :rtype: CurrentFont
        """
        return self._cfont

    def draw_char(self, x, y, ch, color=Colors.WHITE, bg_color=Colors.BLACK):
        """
        Draw a character.

        :param x: Point coordinate (x-axis).
        :type x: int
        :param y: Point coordinate (y-axis).
        :type y: int
        :param ch: The character to draw on the display.
        :type ch: str
        :param color: A 16-bit RGB color (default=white).
        :type color: int
        :param bg_color: Set the character background color (default = black).
        :type bg_color: int
        :return: Width of the character in display pixels.
        :rtype: int
        :raises TFTException: If the a standard font is not set.
        """
        self._is_font_set()
        char_offset = self.__get_offset(ch)

        # Monospaced: Get char width from font.
        if self._cfont.mono_sp:
            char_width = self._cfont.width
        else:
            char_width = self._cfont.font[char_offset]

        char_offset += 1
        # Use autoincrement/decrement feature, if character fits
        # completely on the screen.
        fast_mode = ((x + char_width + 1) < self._max_x
                     and (y + self._cfont.height - 1) < self._max_y)

        # Set character window.
        if fast_mode:
            self._set_window(x, y, x + char_width + 1,
                             y + self._cfont.height - 1)

        self._start_write()

        # Each font "column" (+1 blank column for spacing).
        for i in range(char_width + 1):
            h = 0  # Keep track of char height.

            for j in range(self._cfont.nbrows): # Each column byte.
                if i == char_width:
                    char_data = 0x00  # Insert blank column
                else:
                    char_data = self._cfont.font[char_offset]

                char_offset += 1

                for k in range(8): # Process every row in font character.
                    if h >= self._cfont.height: break

                    if fast_mode:
                        self._write_data(color if self._bit_read(
                            char_data, k) else bg_color)
                    else:
                        self.draw_pixel(x + i, y + (j * 8) + k,
                                        color if self._bit_read(char_data, k)
                                        else bg_color)

                    h += 1

        if fast_mode: self._reset_window()
        self._end_write(reuse=False)
        return char_width

    def draw_text(self, x, y, s, color=Colors.WHITE, bg_color=Colors.BLACK):
        """
        Draw a text string to the display.

        :param x: Point coordinate (x-axis).
        :type x: int
        :param y: Point coordinate (y-axis).
        :type y: int
        :param s: The string to draw on the display.
        :type s: str
        :param color: A 16-bit RGB color (default=white).
        :type color: int
        :param bg_color: Set the character background color (default = black).
        :type bg_color: int
        :return: The position of x after the text is displayed.
        :rtype: int
        """
        currx = x
        self.spi_close_override = True
        self._start_write()

        for k in range(len(s)):
            currx += self.draw_char(currx, y, s[k], color, bg_color) + 1

        self.spi_close_override = False
        self._end_write(reuse=False)
        return currx

    def get_char_extent(self, ch):
        """
        Gets the width and height of a standard font character in pixels.

        .. note:

          The height of a standard character is the same for all characters.

        :param ch: The ASCII character.
        :type ch: str
        :return: A tuple consisting of (width, height).
        :rtype: tuple
        :raises TFTException: If the a standard font is not set.
        """
        self._is_font_set()
        char_offset = self.__get_offset(ch)
        # Get font width from 1st byte
        return self._cfont.font[char_offset], self._cfont.height

    def get_text_extent(self, s):
        """
        Gets the width and height of a standard font string in pixels.

        .. note:

          The height of a standard character is the same for all characters.

        :param s: Text to get the width for.
        :type s: str
        :return: A tuple consisting of (width, height).
        :rtype: tuple
        :raises TFTException: If the a standard font is not set.
        """
        width = 0
        height = 0

        for k in range(len(s)):
            w, h = self.get_char_extent(s[k])
            width += w + 1
            height = h

        return round(width), height

    def __get_offset(self, ch):
        # Bytes used by each character.
        char_offset = (self._cfont.width * self._cfont.nbrows) + 1
        # Char offset (add 4 for font header)
        return (char_offset * (ord(ch) - self._cfont.offset)
                ) + self._CFONT_HEADER_SIZE

    def _is_font_set(self):
        if len(self._cfont.font) <= 0:
            raise TFTException(self.ERROR_MSGS.get('STD_FONT'))

    def _bit_read(self, value, bit):
        """
        Is bit out-of-range for value.

        :param value: The integer value.
        :type value: int
        :param bit: The bit within the value.
        :type bit: int
        :return: A 1 if the bit is within the value range and 0 if
                 out-of-range.
        :rtype: int
        """
        return ((value) >> (bit)) & 0x01
    #
    # End of standard font methods.
    #
    # Beginning of GFX font methods.
    #

    def set_gfx_font(self, font):
        """
        Set the GFX font.

        :param font: GFX font name defined in include file.
        :type font: str
        """
        self._gfx_font = GFXFont(font)

    def draw_gfx_char(self, x, y, ch, color=Colors.WHITE):
        """
        Draw a single character with the current GFX font.

        :param x: Point coordinate (x-axis).
        :type x: int
        :param y: Point coordinate (y-axis).
        :type y: int
        :param ch: A single character to draw on the display.
        :type ch: str
        :param color: A 16-bit RGB color (default=white).
        :type color: int
        :return: The width of character in display pixels.
        :rtype: int
        :raises TFTException: If the a GFX font is not set or a character
                              is not found in the current font.
        """
        self._is_gfx_font_set()
        ch = ord(ch) - self._gfx_font.first

        try:
            glyph = GFXGlyph(self._gfx_font.glyph[ch])
        except IndexError as e:
            ch += self._gfx_font.first
            msg = self.ERROR_MSGS['GFX_BAD_CH'].format(chr(ch))
            raise TFTException(msg)

        bitmap = self._gfx_font.bitmap
        bo = glyph.bitmap_offset
        w = glyph.width
        h = glyph.height
        xa = glyph.x_advance
        xo = glyph.x_offset
        yo = glyph.y_offset
        bits = bit = 0

        # Add character clipping here one day.
        for yy in range(h):
            for xx in range(w):
                if not (bit & 7):
                    bits = bitmap[bo]
                    bo += 1

                bit += 1

                if bits & 0x80:
                    self.draw_pixel(x + xo + xx, y + yo + yy, color)

                bits <<= 1

        return xa

    def draw_gfx_text(self, x, y, s, color=Colors.WHITE, *, add_pixels=0):
        """
        Draw a string in the GFX font.

        :param x: Point coordinate (x-axis).
        :type x: int
        :param y: Point coordinate (y-axis).
        :type y: int
        :param s: The string to draw on the display.
        :type s: str
        :param color: A 16-bit RGB color (default=white).
        :type color: int
        :param add_pixels: Number of pixels to add between characters
                           (Default = 0).
        :type add_pixels: int
        :return: The position of x after the text is displayed.
        :rtype: int
        :raises TFTException: If the a GFX font is not set.
        """
        currx = x
        self.spi_close_override = True
        self._start_write()

        # Draw every character in the string.
        for ch in s:
            currx += self.draw_gfx_char(currx, y, ch, color) + add_pixels

        self.spi_close_override = False
        self._end_write(reuse=False)
        return currx

    def get_gfx_char_extent(self, ch):
        """
        Return the width, height, and the distance to advance cursor for
        the current GFX font.

        .. note::

          If the character does not exist return values gw, gh, and xa
          will be 0 (zero).

        :param ch: The character to draw on the display.
        :type ch: str
        :return: A tuple (gw, gh, xa) where gw is the width in pixels
                 of the character, gh is the height, and xa is the distance
                 to advance cursor on the x axis.
        :rtype: tuple
        :raises TFTException: If the a GFX font is not set.
        """
        self._is_gfx_font_set()
        ch = ord(ch)

        # Is char present in this font?
        if self._gfx_font.first <= ch <= self._gfx_font.last:
            glyph = GFXGlyph(self._gfx_font.glyph[ch - self._gfx_font.first])
            gw = glyph.width
            gh = glyph.height
            xa = glyph.x_advance
        else:
            gw = gh = xa = 0

        return gw, gh, xa

    def get_gfx_text_extent(self, s, *, add_pixels=0):
        """
        Return the width and height of the string in pixels for the
        current GFX font.

        .. note::

          If any of the chararcters in the provided string are not found
          in the font the results for that character will be 0 (zero) for
          both the w and h causing an invalid total for w and h.

        :param s: The character to draw on the display.
        :type s: str
        :param add_pixels: Number of pixels to add between characters
                           (Default = 0).
        :type add_pixels: int
        :return: A tuple (w, h) where w is the width of the string and
                 h is the height.
        :rtype: tuple
        :raises TFTException: If the a GFX font is not set.
        """
        w = h = 0

        for ch in s:
            gw, gh, xa = self.get_gfx_char_extent(ch)
            if gh > h: h = gh
            w += xa + add_pixels

        return w, h

    def _is_gfx_font_set(self):
        if self._gfx_font is None:
            raise TFTException(self.ERROR_MSGS.get('GFX_FONT'))

    #
    # End of GFX font methods.
    #

    def draw_rectangle(self, x0, y0, x1, y1, color):
        """
        Draw a rectangle using rectangular coordinates.

        :param x0: Start point coordinate (x0-axis).
        :type x0: int
        :param y0: Center point coordinate (y0-axis).
        :type y0: int
        :param x1: Center point coordinate (x1-axis).
        :type x1: int
        :param y1: Center point coordinate (y1-axis).
        :type y1: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        self._start_write()
        self.draw_line(x0, y0, x0, y1, color)
        self.draw_line(x0, y0, x1, y0, color)
        self.draw_line(x0, y1, x1, y1, color)
        self.draw_line(x1, y0, x1, y1, color)
        self._end_write(reuse=False)

    def fill_rectangle(self, x0, y0, x1, y1, color):
        """
        Fill a rectangle using rectangular coordinates.

        :param x0: Start point coordinate (x0-axis).
        :type x0: int
        :param y0: Center point coordinate (y0-axis).
        :type y0: int
        :param x1: Center point coordinate (x1-axis).
        :type x1: int
        :param y1: Center point coordinate (y1-axis).
        :type y1: int
        :param color: A 16-bit RGB color
        :type color: int
        """
        self.spi_close_override = True
        self._start_write()
        self._set_window(x0, y0, x1, y1)

        # Count backwards from (y1 - y0 + 1) * (x1 - x0 + 1)) + 1 ending at 1.
        for t in reversed(range(1, round((y1 - y0 + 1) * (x1 - x0 + 1)) + 1)):
            self._write_data(color)

        self._reset_window()
        self.spi_close_override = False
        self._end_write(reuse=False)

    def draw_circle(self, x0, y0, radius, color):
        """
        Draw a circle.

        :param x0: Center point coordinate (x-axis).
        :type x0: int
        :param y0: Center point coordinate (y-axis).
        :type y0: int
        :param radius: The radius of the circle.
        :type radius: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x = 0
        y = radius
        self.spi_close_override = True
        self._start_write()

        self.draw_pixel(x0, y0 + radius, color)
        self.draw_pixel(x0, y0 - radius, color)
        self.draw_pixel(x0 + radius, y0, color)
        self.draw_pixel(x0 - radius, y0, color)

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y

            x += 1
            ddf_x += 2
            f += ddf_x

            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
            self.draw_pixel(x0 + y, y0 + x, color)
            self.draw_pixel(x0 - y, y0 + x, color)
            self.draw_pixel(x0 + y, y0 - x, color)
            self.draw_pixel(x0 - y, y0 - x, color)

        self.spi_close_override = False
        self._end_write(reuse=False)

    def fill_circle(self, x0, y0, radius, color):
        """
        Fill a circle.

        :param x0: Center point coordinate (x-axis).
        :type x0: int
        :param y0: Center point coordinate (y-axis).
        :type y0: int
        :param radius: The radius of the circle.
        :type radius: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x = 0
        y = radius
        self.spi_close_override = True
        self._start_write()

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y

            x += 1
            ddf_x += 2
            f += ddf_x

            self.draw_line(x0 + x, y0 + y, x0 - x, y0 + y, color) # bottom
            self.draw_line(x0 + x, y0 - y, x0 - x, y0 - y, color) # top
            self.draw_line(x0 + y, y0 - x, x0 + y, y0 + x, color) # right
            self.draw_line(x0 - y, y0 - x, x0 - y, y0 + x, color) # left

        self.spi_close_override = False
        self._end_write(reuse=False)
        self.fill_rectangle(x0 - x, y0 - y, x0 + x, y0 + y, color)

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color):
        """
        Draw a triangle using triangular coordinates.

        :param x0: Corner 1 coordinate (x-axis).
        :type x0: int
        :param y0: Corner 1 coordinate (y-axis).
        :type y0: int
        :param x1: Corner 2 coordinate (x-axis).
        :type x1: int
        :param y1: Corner 2 coordinate (y-axis).
        :type y1: int
        :param x2: Corner 3 coordinate (x-axis).
        :type x2: int
        :param y2: Corner 3 coordinate (y-axis).
        :type y2: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        self.spi_close_override = True
        self._start_write()
        self.draw_line(x0, y0, x1, y1, color)
        self.draw_line(x1, y1, x2, y2, color)
        self.draw_line(x2, y2, x0, y0, color)
        self.spi_close_override = False
        self._end_write(reuse=False)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        """
        Fill solid triangle using triangular coordinates.

        :param x0: Corner 1 coordinate (x-axis).
        :type x0: int
        :param y0: Corner 1 coordinate (y-axis).
        :type y0: int
        :param x1: Corner 2 coordinate (x-axis).
        :type x1: int
        :param y1: Corner 2 coordinate (y-axis).
        :type y1: int
        :param x2: Corner 3 coordinate (x-axis).
        :type x2: int
        :param y2: Corner 3 coordinate (y-axis).
        :type y2: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        # Sort coordinates by Y order (y2 >= y1 >= y0)
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        if y1 > y2:
            y2, y1 = y1, y2
            x2, x1 = x1, x2

        ## if y0 > y1:
        ##     y0, y1 = y1, y0
        ##     x0, x1 = x1, x0

        # Handle awkward all-on-same-line case as its own thing.
        if y0 == y2:
            a = b = x0

            if x1 < a: a = x1
            elif x2 > b: b = x1

            if x2 < a: a = x2
            elif x2 > b: b = x2

            self.draw_line(a, y0, b, y0, color)
            return

        dx11 = x1 - x0
        dy11 = y1 - y0
        dx12 = x2 - x0
        dy12 = y2 - y0
        dx22 = x2 - x1
        dy22 = y2 - y1

        # For upper part of triangle, find scanline crossings for segments
        # 0-1 and 0-2. If y1=y2 (flat-bottomed triangle), the scanline y2
        # is included here (and second loop will be skipped, avoiding a /0
        # error there), otherwise scanline y1 is skipped here and handled
        # in the second loop...which also avoids a /0 error here if y0=y1
        # (flat-topped triangle).
        if y1 == y2:
            last = y1     # Include y1 scanline
        else:
            last = y1 - 1 # Skip it

        y = y0
        sa = 0
        sb = 0
        self.spi_close_override = True
        self._start_write()

        while y <= last:
            a = x0 + sa / dy11
            b = x0 + sb / dy12
            sa += dx11
            sb += dx12

            # longhand:
            # a = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            # b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            if a > b: a, b = b, a
            self.draw_line(a, y, b, y, color)
            y += 1

        # For lower part of triangle, find scanline crossings for segments
        # 0-2 and 1-2.  This loop is skipped if y1=y2.
        sa = dx22 * (y - y1)
        sb = dx12 * (y - y0)

        while y <= y2:
            a = x1 + sa / dy22
            b = x0 + sb / dy12
            sa += dx22
            sb += dx12

            # longhand:
            # a = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            # b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            if a > b: a, b = b, a
            self.draw_line(a, y, b, y, color)
            y += 1

        self.spi_close_override = False
        self._end_write(reuse=False)

    def draw_line(self, x0, y0, x1, y1, color):
        """
        Draw a line using rectangular coordinates.

        :param x0: Start point coordinate (x0-axis).
        :type x0: int
        :param y0: Center point coordinate (y0-axis).
        :type y0: int
        :param x1: Center point coordinate (x1-axis).
        :type x1: int
        :param y1: Center point coordinate (y1-axis).
        :type y1: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        # Classic Bresenham algorithm
        steep = abs(y1 - y0) > abs(x1 - x0)

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx / 2

        if y0 < y1:
            ystep = 1
        else:
            ystep = -1

        self._start_write()

        while x0 <= x1:
            if steep:
                self.draw_pixel(y0, x0, color)
            else:
                self.draw_pixel(x0, y0, color)

            err -= dy

            if err < 0:
                y0 += ystep
                err += dx

            x0 += 1

        self._end_write(reuse=False)

    def draw_pixel(self, x0, y0, color):
        """
        Draw a pixel.

        :param x0: Point coordinate (x-axis).
        :type x0: int
        :param y0: Point coordinate (y-axis).
        :type y0: int
        :param color: A 16-bit RGB color.
        :type color: int
        """
        if not ((x0 >= self._max_x) or (y0 >= self._max_y)):
            x0, y0 = self._orient_coordinates(x0, y0)
            self._start_write()
            self._write_register(self.CMD_RAM_ADDR_SET1, x0)
            self._write_register(self.CMD_RAM_ADDR_SET2, y0)
            self._write_register(self.CMD_GRAM_DATA_REG, color)
            self._end_write(reuse=False)

    ## def draw_bitmap(self, x, y, bitmap, w, h, color, bg=Colors.BLACK,
    ##                 transparent=False, x_bit=False):
    ##     """
    ##     Draw a bitmap image.

    ##     :param x: Point coordinate (x-axis).
    ##     :type x: int
    ##     :param y: Point coordinate (y-axis).
    ##     :type y: int
    ##     :param bitmap: A 2D 16-bit color bitmap image to draw on the display.
    ##     :type bitmap: int
    ##     :param w: Width
    ##     :type w: int
    ##     :param h: Height
    ##     :type h: int
    ##     :param color: A 16-bit RGB color (default=white).
    ##     :type color: int
    ##     :param bg: A 16-bit RGB background color.
    ##     :type bg: int
    ##     :param transparent: True = transparent bitmap, False = not transparent.
    ##     :type transparent: bool
    ##     :param x_bit: This indicates that the left most (8th) bit is set.
    ##     :type x_bit: bool
    ##     """
    ##     no_auto_inc = False # Flag set when transparent pixel was 'written'.
    ##     byte_width = (w + 7) / 8
    ##     byte = 0
    ##     mask_bit = 0x01 if x_bit else 0x80

    ##     # Adjust window height/width to display dimensions
    ##     wx0 = 0 if x < 0 else x
    ##     wy0 = 0 if y < 0 else y
    ##     wx1 = (self._max_x if x + w > self._max_x else x + w) - 1
    ##     wy1 = (self._max_y if y + h > self._max_y else y + h) - 1
    ##     wh = wy1 - wy0 + 1

    ##     if self.DEBUG: # pragma: no cover
    ##         print("draw_bitmap: max_x={}, max_y={}".format(
    ##             self._max_x, self._max_y))
    ##         print("draw_bitmap: wx0={}, wy0={}, wx1={}, wy1={}".format(
    ##             wx0, wy0, wx1, wy1))

    ##     self.spi_close_override = True
    ##     self._start_write()
    ##     self._set_window(wx0, wy0, wx1, wy1, AutoIncMode.L2R_TOP_DOWN)

    ##     # for (j = y >= 0 ? 0 : -y; j < (y >= 0 ? 0 : -y)+wh; j++) {...}
    ##     yy = 0 if y >= 0 else -y

    ##     for j in range(yy, yy + wh):
    ##         for i in range(w):
    ##             if i & 7:
    ##                 if x_bit: byte >>= 1
    ##                 else: byte <<= 1
    ##             else:
    ##                 byte = bitmap[j * byte_width + i // 8]

    ##             if wx0 <= x + i <= wx1:
    ##                 # Write only if pixel is within window.
    ##                 if byte & mask_bit:
    ##                     if no_auto_inc:
    ##                         # There was a transparent area,
    ##                         # set pixel coordinates again.
    ##                         self.draw_pixel(x + i, y + j, color)
    ##                         no_auto_inc = False
    ##                     else:
    ##                         self._write_data(color)
    ##                 elif transparent:
    ##                     # No autoincrement in transparent area!
    ##                     no_auto_inc = True
    ##                 else:
    ##                     self._write_data(bg)

    ##     self.spi_close_override = False
    ##     self._end_write(reuse=False)

    def rgb16_to_bgr16(self, color):
        """
        Convert 16-bit RGB to 16-bit BGR color format.

        :param color: A 16-bit RGB color.
        :type color: int
        :return A 16-bit BGR color.
        :rtype: int
        """
        return (
            ((color & 0b1111100000000000) >> 11)
            | (color & 0b0000011111100000)
            | ((color & 0b0000000000011111) << 11)
            )

    def rgb24_to_rgb16(self, red, green, blue):
        """
        Convert 24-bit RGB color components to a 16-bit RGB color.

        :param red: The RED component in the RGB color.
        :type red: int
        :param green: The GREEN component in the RGB color.
        :type green: int
        :param blue: The BLUE component in the RGB color.
        :type blue: int
        :return: An 16-bit RGB color.
        :rtype: int
        """
        return ((round((0x1F * (red + 4)) / 0xFF) << 11) |
                (round((0x3F * (green + 2)) / 0xFF) << 5) |
                round((0x1F * (blue + 4)) / 0xFF))

    def rgb16_to_rgb24(self, color):
        """
        Convert 16-bit RGB color to a 24-bit RGB color components.

        :param color: An RGB 16-bit color.
        :type color: int
        :return: A tuple of the RGB 8-bit components, (red, grn, blu).
        :rtype: tuple
        """
        red = round((0xFF * ((color & 0b1111100000000000) + 4)) / 0x1F) >> 11
        grn = round((0xFF * ((color & 0b0000011111100000) + 2)) / 0x3F) >> 5
        blu = round((0xFF * (color & 0b0000000000011111)) / 0x1F)
        return red, grn, blu

    def _set_window(self, x0, y0, x1, y1, mode=AutoIncMode.TOP_DOWN_L2R):
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

        # Autoincrement mode
        if self.__orientation > 0:
            mode = self._MODE_TAB[self.__orientation - 1][mode]

        self._start_write()
        self._write_register(self.CMD_ENTRY_MODE, 0x1000 | (mode << 3))
        self._write_register(self.CMD_HORIZONTAL_WINDOW_ADDR1, x1)
        self._write_register(self.CMD_HORIZONTAL_WINDOW_ADDR2, x0)
        self._write_register(self.CMD_VERTICAL_WINDOW_ADDR1, y1)
        self._write_register(self.CMD_VERTICAL_WINDOW_ADDR2, y0)

        # Starting position within window and increment/decrement direction
        pos = mode >> 1

        if pos == 0:
            self._write_register(self.CMD_RAM_ADDR_SET1, x1)
            self._write_register(self.CMD_RAM_ADDR_SET2, y1)
        elif pos == 1:
            self._write_register(self.CMD_RAM_ADDR_SET1, x0)
            self._write_register(self.CMD_RAM_ADDR_SET2, y1)
        elif pos == 2:
            self._write_register(self.CMD_RAM_ADDR_SET1, x1)
            self._write_register(self.CMD_RAM_ADDR_SET2, y0)
        elif pos == 3:
            self._write_register(self.CMD_RAM_ADDR_SET1, x0)
            self._write_register(self.CMD_RAM_ADDR_SET2, y0)

        self._write_command(self.CMD_GRAM_DATA_REG)
        self._end_write(reuse=False)

    def _reset_window(self):
        self._start_write()
        self._write_register(self.CMD_HORIZONTAL_WINDOW_ADDR1,
                             self.LCD_WIDTH - 1)
        self._write_register(self.CMD_HORIZONTAL_WINDOW_ADDR2, 0)
        self._write_register(self.CMD_VERTICAL_WINDOW_ADDR1,
                             self.LCD_HEIGHT - 1)
        self._write_register(self.CMD_VERTICAL_WINDOW_ADDR2, 0)
        self._end_write(reuse=False)

    def _write_register(self, command, data):
        self._write_command(command)
        self._write_data(data)

    def _write_command(self, command):
        try:
            self.digital_write(self._rs, self.LOW) # Command
            self.digital_write(self._cs, self.LOW)
            result = self.spi_write(command)
            self.digital_write(self._cs, self.HIGH)
        except CompatibilityException as e: # pragma: no cover
            self._end_write(reuse=False)
            raise e
        else:
            if result is not None:
                result = ','.join(str(v) for v in result)
                result = 'Command: {}\n'.format(result) if self.TESTING else ""
                return self.__write_spi_test_buff(result)

    def _write_data(self, data):
        try:
            self.digital_write(self._rs, self.HIGH) # Data
            self.digital_write(self._cs, self.LOW)
            result = self.spi_write(data)
            self.digital_write(self._cs, self.HIGH)
        except CompatibilityException as e: # pragma: no cover
            self._end_write(reuse=False)
            raise e
        else:
            if result is not None:
                result = ','.join(str(v) for v in result)
                result = '   Data: {}\n'.format(result) if self.TESTING else ""
                return self.__write_spi_test_buff(result)

    def __write_spi_test_buff(self, data):
        if data is not None:
            if not hasattr(self, '_spi_buff'):
                from io import StringIO
                self._spi_buff = StringIO()

            self._spi_buff.write(data)

    def _start_write(self):
        if not self.is_spi_connected:
            self.spi_start_transaction()
            self.digital_write(self._cs, self.LOW)

    def _end_write(self, reuse=True):
        if self.spi_close_override:
            reuse = True

        if not reuse and self.is_spi_connected:
            self.digital_write(self._cs, self.HIGH)
            self.spi_end_transaction()

    def __repr__(self):
        return "<{} object using the {} platform>".format(
            self.__class__.__name__, self.PLATFORM)
