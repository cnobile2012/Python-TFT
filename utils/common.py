# -*- coding: utf-8 -*-
"""
utils/common.py

Common functionality between various TFT controller chips.
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
        ('ARDUINO_STM32_FEATHER', (42000000, 21000000)),
        ('ARDUINO_ARCH_STM32', (16000000,)),
        ('ARDUINO_ARCH_STM32F1', (18000000,)),
        ('STM32F1', (0,)),
        ('ARDUINO_FEATHER52', (0,)),
        ('TEENSYDUINO', (8000000,)),
        ('ESP8266', (40000000, 40000000)),
        ('ESP32', (40000000, 40000000)),
        ('RASPI', (31200000, 31200000)),
        ('COMPUTER', (80000000,)),
        )
    # {1: ('ARDUINO_STM32_FEATHER', (42000000, 21000000)), ...}
    _BOARDS = {idx: (name, freq)
               for idx, (name, freq) in enumerate(_BOARD_SPECS, start=1)}
    # {'ARDUINO_STM32_FEATHER': 1, ...}
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
        return board_spec[0] if board_spec is not None else 'Undefined Board'

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


class _BGR16BitColor:
    """
    BGR 16-bit color table definition (BGR565)
    """
    RGB_TO_BGR = lambda self, c: (
        ((c & 0b1111100000000000) >> 11)
        | (c & 0b0000011111100000)
        | ((c & 0b0000000000011111) << 11)
        )

    def __init__(self, rgb_class=RGB16BitColor):
        """
        Constructor

        Dynamically creates BGR member objects from the an RGB class.

        :param rgb_class: The RGB 16-bit class object
                          (default is RGB16BitColor).
        :type rgb_class: <class object>
        """
        class_name = rgb_class.__qualname__
        bgr_colors = {c: self.RGB_TO_BGR(eval("{}.{}".format(class_name, c)))
                      for c in dir(rgb_class) if not c.startswith("_")}
        [exec("_BGR16BitColor.{} = {}".format(c, v), globals())
         for c, v in bgr_colors.items()]

BGR16BitColor = _BGR16BitColor()
