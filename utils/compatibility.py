# -*- coding: utf-8 -*-
"""
compatibility.py

This class defines a generic compatibility class to normalize between
different versions of Python. i.e. C standard, MicroPython, and CircuitPython

We need to test for the existance of a few methods and functions then decide
which to use in this library.
"""

class CompatibilityException(Exception):
    pass


MP = 1 # MicroPython
CP = 2 # CircuitPython
RP = 3 # Raspberry Pi or any Other >= 3.5 Python
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


class Boards:
    ARDUINO_STM32_FEATHER = 1
    ARDUINO_ARCH_STM32 = 2
    ARDUINO_ARCH_STM32F1 = 3
    STM32F1 = 4
    ARDUINO_FEATHER52 = 5
    TEENSYDUINO = 6
    ESP8266 = 7
    ESP32 = 8
    RASPI = 9


class Compatibility:
    """
    Checks the compatibility and version of Python.
    """
    PLATFORM = None

    def platform(self, platform):
        if platform not in {v: k for k, v in Boards.__dict__.items()
                            if not k.startswith('__')}:
            raise CompatibilityException(
                'Error: The {} board is not supported.'.format(platform))

        self.PLATFORM = platform

    def _delay(self, ms):
        if PYTHON_VERSION in (MP, CP):
            sleep_ms(ms)
        elif PYTHON_VERSION == RP:
            sleep(ms/1000) # Convert to floating point.
