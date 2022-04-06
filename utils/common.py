# -*- coding: utf-8 -*-
"""
utils/common.py

Common functionality between ILI chips.
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
