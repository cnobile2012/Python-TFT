# -*- coding: utf-8 -*-
"""
utils/common.py

Common functionality between ILI chips.
"""

class RGB16BitColor:
    """
    RGB 16-bit color table definition (RG565)
    """
    COLOR_BLACK       = 0x0000  #   0,   0,   0
    COLOR_WHITE       = 0xFFFF  # 255, 255, 255
    COLOR_BLUE        = 0x001F  #   0,   0, 255
    COLOR_GREEN       = 0x07E0  #   0, 255,   0
    COLOR_RED         = 0xF800  # 255,   0,   0
    COLOR_NAVY        = 0x000F  #   0,   0, 128
    COLOR_DARKBLUE    = 0x0011  #   0,   0, 139
    COLOR_DARKGREEN   = 0x03E0  #   0, 128,   0
    COLOR_DARKCYAN    = 0x03EF  #   0, 128, 128
    COLOR_CYAN        = 0x07FF  #   0, 255, 255
    COLOR_TURQUOISE   = 0x471A  #  64, 224, 208
    COLOR_INDIGO      = 0x4810  #  75,   0, 130
    COLOR_DARKRED     = 0x8000  # 128,   0,   0
    COLOR_OLIVE       = 0x7BE0  # 128, 128,   0
    COLOR_GRAY        = 0x8410  # 128, 128, 128
    COLOR_GREY        = 0x8410  # 128, 128, 128
    COLOR_SKYBLUE     = 0x867D  # 135, 206, 235
    COLOR_BLUEVIOLET  = 0x895C  # 138,  43, 226
    COLOR_LIGHTGREEN  = 0x9772  # 144, 238, 144
    COLOR_DARKVIOLET  = 0x901A  # 148,   0, 211
    COLOR_YELLOWGREEN = 0x9E66  # 154, 205,  50
    COLOR_BROWN       = 0xA145  # 165,  42,  42
    COLOR_DARKGRAY    = 0x7BEF  # 128, 128, 128
    COLOR_DARKGREY    = 0x7BEF  # 128, 128, 128
    COLOR_SIENNA      = 0xA285  # 160,  82,  45
    COLOR_LIGHTBLUE   = 0xAEDC  # 172, 216, 230
    COLOR_GREENYELLOW = 0xAFE5  # 173, 255,  47
    COLOR_SILVER      = 0xC618  # 192, 192, 192
    COLOR_LIGHTGRAY   = 0xC618  # 192, 192, 192
    COLOR_LIGHTGREY   = 0xC618  # 192, 192, 192
    COLOR_LIGHTCYAN   = 0xE7FF  # 224, 255, 255
    COLOR_VIOLET      = 0xEC1D  # 238, 130, 238
    COLOR_AZUR        = 0xF7FF  # 240, 255, 255
    COLOR_BEIGE       = 0xF7BB  # 245, 245, 220
    COLOR_MAGENTA     = 0xF81F  # 255,   0, 255
    COLOR_TOMATO      = 0xFB08  # 255,  99,  71
    COLOR_GOLD        = 0xFEA0  # 255, 215,   0
    COLOR_ORANGE      = 0xFD20  # 255, 165,   0
    COLOR_SNOW        = 0xFFDF  # 255, 250, 250
    COLOR_YELLOW      = 0xFFE0  # 255, 255,   0
