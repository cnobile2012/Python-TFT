# Test file

class ILI9225:
    """
    Main ILI9225 class.
    """
    CMD_GAMMA_CTRL10            = 0x59  # Gamma Control 10

    SOME_LIST = [
        0x06, 0x00, 0x24, 0x7E, 0x24, 0x7E, 0x24,  # Code for char #
    ]

    # 1: pixel width of 1 font character, 2: pixel height
    _CFONT_HEADER_SIZE = 4

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
