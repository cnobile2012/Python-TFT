# -*- coding: utf-8 -*-

from .default_fonts import (Terminal6x8, Terminal11x16, Terminal12x16,
                            Trebuchet_MS16x21)
from .common import RGB16BitColor, BGR16BitColor
from .compatibility import Boards

__all__ = (
    'Terminal6x8', 'Terminal11x16', 'Terminal12x16', 'Trebuchet_MS16x21',
    'RGB16BitColor', 'BGR16BitColor',
    'Boards',
    'TFTException', 'CompatibilityException'
    )


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
