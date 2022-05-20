# -*- coding: utf-8 -*-
"""
utils/compatibility.py

This class defines a generic compatibility class to normalize between
different versions of Python. i.e. C standard, MicroPython, and CircuitPython

We need to test for the existance of a few methods and functions then decide
which to use in this library.
"""

try: # MicroPython
    from time import sleep_ms
except:
    try: # CircuitPython
        from uasyncio import sleep_ms
    except:
        try: # A PC with the RTx.GPIO library and hardware
            import RTk
        except:
            try: # Raspberry Pi
                import importlib
            except: # pragma: no cover
                pass
            else:
                from py_versions.raspberrypi import PiVersion
        else: # pragma: no cover
            from py_versions.computer import PiVersion
    else: # pragma: no cover
        from py_versions.circuitpython import PiVersion
else: # pragma: no cover
    from py_versions.micropython import PiVersion


class Boards:
    # With MCUs
    ARDUINO_STM32_FEATHER = 1
    ARDUINO_ARCH_STM32 = 2
    ARDUINO_ARCH_STM32F1 = 3
    STM32F1 = 4
    ARDUINO_FEATHER52 = 5
    RP2040 = 6
    TEENSYDUINO = 7
    ESP8266 = 8
    ESP32 = 9
    #ESP32_C3 = 10
    # With CPUs
    RASPI = 50
    COMPUTER = 51
    # Architectures
    AVR = 70
    ARM = 71

    _BOARDS = {
        ARDUINO_STM32_FEATHER: 'ARDUINO_STM32_Reather',
        ARDUINO_ARCH_STM32: 'ARDUINO_ARCH_STM32',
        ARDUINO_ARCH_STM32F1: 'ARDUINO_ARCH_STM32F1',
        STM32F1: 'STM32F1',
        ARDUINO_FEATHER52: 'ARDUINO_FEATHER52',
        TEENSYDUINO: 'TEENSYDUINO',
        ESP8266: 'ESP8266',
        ESP32: 'ESP32',
        RASPI: 'RASPI',
        COMPUTER: 'COMPUTER',
        AVR: 'AVR',
        ARM: 'ARM'
        }

    _FREQUENCY = {
        ARDUINO_ARCH_STM32: 16000000,
        ARDUINO_ARCH_STM32F1: 18000000,
        AVR: 8000000,
        COMPUTER: 80000000,
        RP2040: 1000000,
        ESP8266: 40000000,
        ESP32: 40000000,
        RASPI: 31200000, # RPi 3?
        TEENSYDUINO: 8000000,
        }

    @staticmethod
    def get_frequency(board):
        return Boards._FREQUENCY.get(board, 24000000)


class Compatibility(PiVersion):
    """
    Checks the compatibility and version of Python.
    """
    _SPI_PD_ERR_MSG = 'Invalid pin selection for hardware SPI.'

    def __init__(self, mode=None):
        if not None:
            super().__init__(mode)

        self.BOARD = None

    def _get_board_name(self, board=None):
        board = 1000 if board is None and self.BOARD is None else board
        board = board if board is not None else self.BOARD
        return Boards._BOARDS.get(board, "Unknown board")

    def get_board(self):
        return self.BOARD

    def set_board(self, board):
        """
        Set the board as defined in the Boards class.

        :param board: The board to use.
        :type board: int
        :raise CompatibilityException: If the board is unsupported.
        """
        from utils import CompatibilityException

        board_name = self._get_board_name(board)

        if board_name not in [v for v in dir(Boards) if not v.startswith('_')]:
            raise CompatibilityException(
                self.ERROR_MSGS['BRD_UNSUP'].format(board_name))

        self.BOARD = board
