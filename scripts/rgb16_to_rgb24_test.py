#!/usr/bin/env python

from utils import RGB16BitColor as Colors


def rgb16_to_rgb24(color):
    """
    Convert 16-bit RGB color to a 24-bit RGB color components.

    :param color: An RGB 16-bit color.
    :type color: int
    :return: A tuple of the RGB 8-bit components, (red, grn, blu).
    :rtype: tuple
    """
    #red = (color & 0b1111100000000000) >> 11 << 3
    #grn = (color & 0b0000011111100000) >> 5 << 2
    #blu = (color & 0b0000000000011111) << 3

    red = round((0xFF * ((color & 0b1111100000000000) + 4)) / 0x1F) >> 11
    grn = round((0xFF * ((color & 0b0000011111100000) + 2)) / 0x3F) >> 5
    blu = round((0xFF * (color & 0b0000000000011111)) / 0x1F)
    return red, grn, blu


def rgb24_to_rgb16(red, green, blue):
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
    #return ((red >> 3) << 11) | ((green >> 2) << 5) | (blue >> 3)
    return ((round((0x1F * (red + 4)) / 0xFF) << 11) |
            (round((0x3F * (green + 2)) / 0xFF) << 5) |
            round((0x1F * (blue + 4)) / 0xFF))


rgb16_red = Colors.RED
rgb24_red = 0xFF0000
found_components = rgb16_to_rgb24(rgb16_red)
print(f"RED should be {hex(rgb24_red)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"RED should be {hex(rgb16_red)} found {hex(found_color)}\n")

rgb16_blu = Colors.BLUE
rgb24_blu = 0x0000FF
found_components = rgb16_to_rgb24(rgb16_blu)
print(f"BLUE should be {hex(rgb24_blu)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"BLUE should be {hex(rgb16_blu)} found {hex(found_color)}\n")

rgb16_yel = Colors.YELLOW
rgb24_yel = 0xFFFF00
found_components = rgb16_to_rgb24(rgb16_yel)
print(f"YELLOW should be {hex(rgb24_yel)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"YELLOW should be {hex(rgb16_yel)} found {hex(found_color)}\n")

rgb16_cyn = Colors.CYAN
rgb24_cyn = 0x00FFFF
found_components = rgb16_to_rgb24(rgb16_cyn)
print(f"CYAN should be {hex(rgb24_cyn)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"CYAN should be {hex(rgb16_cyn)} found {hex(found_color)}\n")

rgb16_gra = Colors.GRAY
rgb24_gra = 0x808080
found_components = rgb16_to_rgb24(rgb16_gra)
print(f"GRAY should be {hex(rgb24_gra)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"GRAY should be {hex(rgb16_gra)} found {hex(found_color)}\n")

rgb16_wht = Colors.WHITE
rgb24_wht = 0xFFFFFF
found_components = rgb16_to_rgb24(rgb16_wht)
print(f"WHITE should be {hex(rgb24_wht)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"WHITE should be {hex(rgb16_wht)} found {hex(found_color)}\n")

rgb16_blk = Colors.BLACK
rgb24_blk = 0x000000
found_components = rgb16_to_rgb24(rgb16_blk)
print(f"BLACK should be {hex(rgb24_blk)} found "
      f"{[hex(x) for x in found_components]}")
found_color = rgb24_to_rgb16(*found_components)
print(f"BLACK should be {hex(rgb16_blk)} found {hex(found_color)}\n")
