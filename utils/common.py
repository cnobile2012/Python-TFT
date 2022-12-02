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


class CommonMethods:
    """
    These are common method accross all display types.
    """
    # Orientation modes
    MODE_R2L_BOTTOM_UP = 0
    MODE_BOTTOM_UP_R2L = 1
    MODE_L2R_BOTTOM_UP = 2
    MODE_BOTTOM_UP_L2R = 3
    MODE_R2L_TOP_DOWN = 4
    MODE_TOP_DOWN_R2L = 5
    MODE_L2R_TOP_DOWN = 6
    MODE_TOP_DOWN_L2R = 7

    # Corresponding modes when orientation changes.
    _MODE_TAB = (
        (MODE_BOTTOM_UP_L2R, MODE_L2R_BOTTOM_UP,
         MODE_TOP_DOWN_L2R, MODE_L2R_TOP_DOWN,
         MODE_BOTTOM_UP_R2L, MODE_R2L_BOTTOM_UP,
         MODE_TOP_DOWN_R2L, MODE_R2L_TOP_DOWN), # 90°
        (MODE_L2R_TOP_DOWN, MODE_TOP_DOWN_L2R,
         MODE_R2L_TOP_DOWN, MODE_TOP_DOWN_R2L,
         MODE_L2R_BOTTOM_UP, MODE_BOTTOM_UP_L2R,
         MODE_R2L_BOTTOM_UP, MODE_BOTTOM_UP_R2L), # 180°
        (MODE_TOP_DOWN_R2L, MODE_R2L_TOP_DOWN,
         MODE_BOTTOM_UP_R2L, MODE_R2L_BOTTOM_UP,
         MODE_TOP_DOWN_L2R, MODE_L2R_TOP_DOWN,
         MODE_BOTTOM_UP_L2R, MODE_L2R_BOTTOM_UP) # 270°
        )

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

    def clear(self, x0=None, y0=None, x1=None, y1=None,
              color=RGB16BitColors.BLACK):
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
