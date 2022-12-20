# -*- coding: utf-8 -*-
"""
utils/common.py

Common functionality between various TFT controller chips.

These sites list boards and their MCUs.
https://techexplorations.com/guides/esp32/micropython-with-the-esp32/4-micropython-compatible-boards/
https://stm32-base.org/boards/
"""


class TFTException(Exception):
    """
    Raised when an error is found in the main TFT class.
    """
    pass


class CompatibilityException(Exception):
    """
    Raised when there is a compatability error.
    """
    pass


class _Boards:
    _BOARD_SPECS = (
        # WiPy
        ('CC32xx', (20000000,)),
        #('COMPUTER', (80000000,)),
        ('ESP8266', (60000000, 60000000)),
        ('ESP32', (60000000, 60000000)),
        # BBC Micro:bit
        ('NRF52', (32000000, 32000000, 32000000, 32000000,)),
        # Raspberry Pi
        ('RASPI', (80000000, 80000000)),
        # RPi Pico, Feather 2040, ItsyBitsy 2040, Tiny 2040, XIAO-RPi, etc.
        ('RP2040', (65200000, 65200000)),
        ('SAMD20', (8000000,)),
        # Seeeduino XIAO SAMD21G18
        ('SAMD21', (12000000,)),
        # Some Blue Pill boards and many others.
        ('STM32F0', (18000000, 18000000)),
        # Black Pill and some Blue Pill boards and others.
        ('STM32F1', (18000000, 18000000, 18000000)),
        # WaveShare Core205R
        ('STM32F2', (30000000, 30000000, 30000000)),
        # RobotDyn Black Pill and others.
        ('STM32F3', (18000000, 18000000, 18000000)),
        # Pyboard v1.1, WeAct Black Pill and others.
        ('STM32F4', (42000000, 21000000, 21000000)),
        # Pyboard D-series
        ('STM32F72', (50000000, 25000000, 25000000, 50000000, 50000000)),
        # Pyboard D-series
        ('STM32F76', (54000000, 25000000, 25000000, 54000000, 54000000,
                      54000000)),
        )
    # {1: ('STM32', (42000000, 21000000)), ...}
    _BOARDS = {idx: (name, freq)
               for idx, (name, freq) in enumerate(_BOARD_SPECS, start=1)}
    # {'STM32': 1, ...}
    _BOARD_IDS = {spec[0]: idx for idx, spec in _BOARDS.items()}

    def __init__(self):
        [setattr(self, name, idx) for name, idx in self._BOARD_IDS.items()]

    @staticmethod
    def get_board_name(board_id):
        """
        Get the board name. This is the text identifier used in thsi API
        for the board.

        :param board_id: The numerical board ID.
        :type board_id: int
        :return: The text that identifiee the board.
        :rtype: str
        """
        board_spec = Boards._BOARDS.get(board_id)
        return board_spec[0] if board_spec is not None else 'Undefined'

    @staticmethod
    def get_board_id(board_name):
        """
        Get the board ID. This is a numerical ID.

        :param board_name: The text that identifiee the board.
        :type board_name: str
        :return: The numerical board ID.
        :rtype: int
        """
        return Boards._BOARD_IDS.get(board_name, 0)

    @staticmethod
    def get_frequency(board_id, port):
        """
        Get the SPI frequency based on the board and the SPI port used.

        :param board_id: The numerical board ID.
        :type board_id: int
        :param port: The port ID.
        :type port: int
        :return: The SPI frequency.
        :rtype: int
        """
        board_spec = Boards._BOARDS.get(board_id)
        return board_spec[1][port] if board_spec is not None else 0

Boards = _Boards()


class RGB16BitColor:
    """
    RGB 16-bit color table definition (RGB565)
    """
    BLACK       = 0x0000  #   0,   0,   0
    WHITE       = 0xFFFF  # 255, 255, 255
    BLUE        = 0x001F  #   0,   0, 255
    GREEN       = 0x07E0  #   0, 255,   0
    RED         = 0xF800  # 255,   0,   0
    NAVY        = 0x000F  #   0,   0, 128
    DARKBLUE    = 0x0011  #   0,   0, 139
    DARKGREEN   = 0x03E0  #   0, 128,   0
    DARKCYAN    = 0x03EF  #   0, 128, 128
    CYAN        = 0x07FF  #   0, 255, 255
    TURQUOISE   = 0x471A  #  64, 224, 208
    INDIGO      = 0x4810  #  75,   0, 130
    DARKRED     = 0x8000  # 128,   0,   0
    OLIVE       = 0x7BE0  # 128, 128,   0
    GRAY        = 0x8410  # 128, 128, 128
    GREY        = 0x8410  # 128, 128, 128
    SKYBLUE     = 0x867D  # 135, 206, 235
    BLUEVIOLET  = 0x895C  # 138,  43, 226
    LIGHTGREEN  = 0x9772  # 144, 238, 144
    DARKVIOLET  = 0x901A  # 148,   0, 211
    YELLOWGREEN = 0x9E66  # 154, 205,  50
    BROWN       = 0xA145  # 165,  42,  42
    DARKGRAY    = 0x7BEF  # 128, 128, 128
    DARKGREY    = 0x7BEF  # 128, 128, 128
    SIENNA      = 0xA285  # 160,  82,  45
    LIGHTBLUE   = 0xAEDC  # 172, 216, 230
    GREENYELLOW = 0xAFE5  # 173, 255,  47
    SILVER      = 0xC618  # 192, 192, 192
    LIGHTGRAY   = 0xC618  # 192, 192, 192
    LIGHTGREY   = 0xC618  # 192, 192, 192
    LIGHTCYAN   = 0xE7FF  # 224, 255, 255
    VIOLET      = 0xEC1D  # 238, 130, 238
    AZUR        = 0xF7FF  # 240, 255, 255
    BEIGE       = 0xF7BB  # 245, 245, 220
    MAGENTA     = 0xF81F  # 255,   0, 255
    TOMATO      = 0xFB08  # 255,  99,  71
    GOLD        = 0xFEA0  # 255, 215,   0
    ORANGE      = 0xFD20  # 255, 165,   0
    SNOW        = 0xFFDF  # 255, 250, 250
    YELLOW      = 0xFFE0  # 255, 255,   0


## class _BGR16BitColor:
##     """
##     BGR 16-bit color table definition (BGR565)
##     """
##     RGB_TO_BGR = lambda self, c: (
##         ((c & 0b1111100000000000) >> 11)
##         | (c & 0b0000011111100000)
##         | ((c & 0b0000000000011111) << 11)
##         )

##     def __init__(self, rgb_class=RGB16BitColor):
##         """
##         Constructor

##         Dynamically creates BGR member objects from the an RGB class.

##         :param rgb_class: The RGB 16-bit class object
##                           (default is RGB16BitColor).
##         :type rgb_class: <class object>
##         """
##         class_name = rgb_class.__qualname__
##         bgr_colors = {c: self.RGB_TO_BGR(eval("{}.{}".format(class_name, c)))
##                       for c in dir(rgb_class) if not c.startswith("_")}
##         [exec("_BGR16BitColor.{} = {}".format(c, v), globals())
##          for c, v in bgr_colors.items()]

## BGR16BitColor = _BGR16BitColor()


Colors = RGB16BitColor


class CommonMethods:
    """
    These are common method accross all display types.
    """

    ERROR_MSGS = {
        'STD_FONT': "Please set a standard font before using this method.",
        'GFX_FONT': "Please set a GFX font before using this method.",
        'GFX_BAD_CH': "The character '{}' is not in the current font.",
        'BRD_UNSUP': "Error: The {} board is not supported.",
        'INV_PORT': "Invalid port for the {} board."
        }

    def __init__(self):
        self._max_x = 0
        self._max_y = 0
        self.__orientation = 0
        self.__brightness = 0
        self.__spi_close_override = False

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
        self.fill_rectangle(0, 0, self.max_x - 1, self.max_y - 1, color)
        self.orientation = old_orientation
        self.delay(10)

    def set_backlight(self, flag, brightness=None):
        """
        Set the backlight on or off and set the brightness if there
        is an LED pin.

        :param flag: True = backlight on and False = backlight off.
        :type flag: bool
        :param brightness: The brightness of the display, it defaults to
                           full brightness.
        :type brightness: int
        """
        # This fixes the subclass issue where MAX_BRIGHTNESS is not
        # available until instantiation.
        brightness = self.MAX_BRIGHTNESS if brightness is None else brightness

        self._bl_state = flag

        if self._led != -1:
            self.brightness = brightness
            self.change_led_duty_cycle(
                self.brightness if self._bl_state else 0)

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
            y = self.max_y - y - 1
            x, y = y, x
        elif self.__orientation == 2:
            x = self.max_x - x - 1
            y = self.max_y - y - 1
        elif self.__orientation == 3:
            x = self.max_x - x - 1
            x, y = y, x

        # if self.__orientation == 0: We fall through.
        return x, y

    @property
    def max_x(self):
        """
        Get the display max x size. The valueis based on the orientation.

        .. note::

          Either 0..176 or 0..220 depending on orientation.

        :return: Horizontal size of the display in pixels.
        :rtype: int
        """
        return self._max_x

    @property
    def max_y(self):
        """
        Get the display max y size. The value is based on the orientation.

        .. note::

          Either 0..176 or 0..220 depending on orientation.

        :return: Vertical size of the display in pixels.
        :rtype: int
        """
        return self._max_y

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
        array = bytearray()
        c_hi = color >> 8
        c_lo = color & 0xFF

        # Count backwards from (y1 - y0 + 1) * (x1 - x0 + 1)) + 1 ending at 1.
        for t in reversed(range(1, round((y1 - y0 + 1) * (x1 - x0 + 1)) + 1)):
            if (hasattr(self, '_need_chunking')
                and self._need_chunking(array)): # pragma: no cover
                self._write_data(array)
                array = bytearray()

            array.append(c_hi)
            array.append(c_lo)

        self._write_data(array)
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
        pixels = []
        self.spi_close_override = True
        self._start_write()

        pixels.append((x0, y0 + radius, color))
        pixels.append((x0, y0 - radius, color))
        pixels.append((x0 + radius, y0, color))
        pixels.append((x0 - radius, y0, color))

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y

            x += 1
            ddf_x += 2
            f += ddf_x

            pixels.append((x0 + x, y0 + y, color))
            pixels.append((x0 - x, y0 + y, color))
            pixels.append((x0 + x, y0 - y, color))
            pixels.append((x0 - x, y0 - y, color))
            pixels.append((x0 + y, y0 + x, color))
            pixels.append((x0 - y, y0 + x, color))
            pixels.append((x0 + y, y0 - x, color))
            pixels.append((x0 - y, y0 - x, color))

        self.draw_pixel_alt(pixels)
        self._end_write(reuse=False)
        self.spi_close_override = False

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

        pixels = []
        self._start_write()

        while x0 <= x1:
            if steep:
                pixels.append((y0, x0, color))
            else:
                pixels.append((x0, y0, color))

            err -= dy

            if err < 0:
                y0 += ystep
                err += dx

            x0 += 1

        self.draw_pixel_alt(pixels)
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
    ##     wx1 = (self.max_x if x + w > self.max_x else x + w) - 1
    ##     wy1 = (self.max_y if y + h > self.max_y else y + h) - 1
    ##     wh = wy1 - wy0 + 1

    ##     if self.DEBUG: # pragma: no cover
    ##         print("draw_bitmap: max_x={}, max_y={}".format(
    ##             self.max_x, self.max_y))
    ##         print("draw_bitmap: wx0={}, wy0={}, wx1={}, wy1={}".format(
    ##             wx0, wy0, wx1, wy1))

    ##     self.spi_close_override = True
    ##     self._start_write()
    ##     self._set_window(wx0, wy0, wx1, wy1, self.MODE_L2R_TOP_DOWN)

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

    ##     self._reset_window()
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

    def _write_register(self, command, data):
        self._write_command(command)
        self._write_data(data)

    def _write_command(self, command):
        try:
            self.digital_write(self._rs, self.LOW) # Command
            self.spi_write(command)
        except CompatibilityException as e: # pragma: no cover
            self._end_write(reuse=False)
            raise e

    def _write_data(self, data):
        try:
            self.digital_write(self._rs, self.HIGH) # Data
            self.spi_write(data)
        except CompatibilityException as e: # pragma: no cover
            self._end_write(reuse=False)
            raise e

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
