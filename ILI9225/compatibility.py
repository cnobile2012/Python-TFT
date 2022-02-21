# -*- coding: utf-8 -*-
"""
compatibility.py

This class defines a generic compatibility class to normalize between
different versions of Python. i.e. C standard, MicroPython, and CircuitPython

We need to test for the existance of a few methods and functions then decide
which to use in this library.
"""

MP = 1
CP = 2
RP = 3
PYTHON_VERSION = 0

try:
    from time import sleep_ms
except:
    try:
        from uasyncio import sleep_ms
    except:
        try:
            import importlib
            from time import sleep
        except:
            pass
        else:
            PYTHON_VERSION = RP
    else:
        PYTHON_VERSION = CP
else:
    PYTHON_VERSION = MP


class Compatibility:
    """
    Checks the compatibility and version of Python.
    """

    def _delay(self, ms):
        if PYTHON_VERSION in (MP, CP):
            sleep_ms(ms)
        elif PYTHON_VERSION == RP:
            sleep(ms/1000) # Convert to floating point.


