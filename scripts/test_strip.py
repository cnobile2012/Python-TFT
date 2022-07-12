# -*- coding: utf-8 -*-
# Test file

"""
Discription text, but should not be in the resultant file.
"""


SansSerif_plain_10Bitmaps = [
        # Bitmap Data:
        0x00, # ' '
        0xAA,0x88, # '!'
        0xAA,0xA0, # '"'
        0x24,0x24,0x7E,0x28,0xFC,0x48,0x48, # '#'
        0x21,0xEA,0x38,0x38,0xAF,0x08, # '$'
        0xE4,0x52,0x2A,0x1F,0xE1,0x51,0x28,0x9C, # '%'
        0x30,0x48,0x40,0xB2,0x8A,0xCC,0x72, # '&'
        0xA8, # '''
        0x52,0x49,0x24,0x40, # '('
        0x91,0x24,0x94,0x80, # ')'
        0xA9,0xC7,0x2A, # '#'
]


class ILI9225:
    """
    Main ILI9225 class.
    """
    CMD_GAMMA_CTRL10            = 0x59  # Gamma Control 10

    # 1: pixel width of 1 font character, 2: pixel height
    _CFONT_HEADER_SIZE = 4

    _MODE_TAB = (
        (AutoIncMode.L2R_TOP_DOWN, AutoIncMode.TOP_DOWN_L2R,
         AutoIncMode.R2L_BOTTOM_UP, AutoIncMode.BOTTOM_UP_R2L), # 180°
        (AutoIncMode.TOP_DOWN_R2L, AutoIncMode.R2L_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_L2R, AutoIncMode.L2R_BOTTOM_UP) # 270°
        )

    def __init__(self, rst, rs, spi_port, cs, led=-1, board=None, *,
                 brightness=MAX_BRIGHTNESS, rpi_mode=None):
        """
        Initialize the ILI9225 class.

        :param rst: The RST (reset) pin on the display. (RTD on some devices.)
        :type rst: int
        :param rs: The RS (command/data) pin on the display. 0: command, 1: data
        :type rs: int
        :param spi_port: The SPI port to use on the board.
        :type spi_port: int
        :param cs: The CS (chip select) pin on the display.
        :type cs: int
        :param led: The LED pin on the display.
        :type led: int
        :param brightness: Set the brightness from 0..255 (default=255).
        :type brightness: int
        :param board: The board this will run on. e.g. Boards.ESP32
        :type board: int
        :param rpi_mode: Only applies to the Raspberry Pi and Computer boards.
                         Default GPIO.BCM
        :type rpi_mode: int
        :raises CompatibilityException: If the board is unsupported.
        """
        super().__init__(rpi_mode=rpi_mode)
        self._rst = rst
        self.__brightness = 0
        self.brightness = brightness # Default it maximum brightness.
        self.set_board(board)
        src = '''
        Garbage but must keep it.
        And this line also.
        '''
        duh = """
        This # needs to stay
        # So does this one
        """
        self.hash_code = "Test a hash # some comment "
        # commented code # Comment

    #
    # Comment to get rid of
    #

    @property
    def spi_close_override(self):
        # Another comment to get rid of
        src = "# is used in code so keep it."
        return self.__spi_close_override

    @spi_close_override.setter
    def spi_close_override(self, value):
        src = '''
        Garbage but must keep it.
        And this line also.
        '''
        self.__spi_close_override = value

    ## def draw_bitmap(self, x, y, bitmap, w, h, color, bg=Colors.BLACK,
    ##                 transparent=False, x_bit=False):
    ##     """
    ##     Draw a bitmap image.

    ##     :param x: Point coordinate (x-axis).
    ##     :type x: int
    ##     :param x_bit: This indicates that the left most (8th) bit is set.
    ##     :type x_bit: bool
    ##     """
    ##     no_auto_inc = False # Flag set when transparent pixel was 'written'.
    ##     byte_width = (w + 7) / 8
    ##     byte = 0
    ##     mask_bit = 0x01 if x_bit else 0x80

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
