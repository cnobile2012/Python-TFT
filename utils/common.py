# -*- coding: utf-8 -*-
"""
utils/common.py

Common functionality between various TFT controller chips.
"""

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
