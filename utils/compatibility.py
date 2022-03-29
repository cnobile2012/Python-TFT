# -*- coding: utf-8 -*-
"""
utils/compatibility.py

This class defines a generic compatibility class to normalize between
different versions of Python. i.e. C standard, MicroPython, and CircuitPython

We need to test for the existance of a few methods and functions then decide
which to use in this library.
"""

class CompatibilityException(Exception):
    pass


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
            except:
                pass
            else:
                from py_versions.raspberrypi import PiVersion
        else:
            from py_versions.computer import PiVersion
    else:
        from py_versions.circuitpython import PiVersion
else:
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
        RASPI: 35000000, # RPi 3?
        TEENSYDUINO: 8000000,
        }

    _MSBFIRST = {} # Seems to be 1 for eveything.

    _SPI_MODE0 = {}

    @staticmethod
    def get_frequency(board):
        return Boards._FREQUENCY.get(board, 24000000)

    @staticmethod
    def get_msbfirst(board):
        return Boards._MSBFIRST.get(board, 1) 


class Compatibility(PiVersion):
    """
    Checks the compatibility and version of Python.
    """

    def __init__(self, mode=None):
        if not None:
            super().__init__(mode)

        self.BOARD = None
        self._spi = None

    def _get_board_name(self, board=None):
        board = board if board is not None else self.BOARD
        return Boards._BOARDS.get(board, "Unknown board")

    def get_board(self):
        return self.BOARD

    def set_board(self, board):
        board_name = self._get_board_name(board)

        if board_name not in [v for v in dir(Boards) if not v.startswith('_')]:
            raise CompatibilityException(
                "Error: The {} board is not supported.".format(board_name))

        self.BOARD = board

    def spi_port_device(self, clock, mosi, miso, select):
        """
        Convert a mapping of pin definitions, which must contain 'clock',
        and 'select' at a minimum, to a hardware SPI port, device tuple.
        Raises `CompatibilityException` if the pins do not represent a valid
        hardware SPI device.
        """
        # The port variable is sometimes refered to as the bus.
        for port, pins in self._SPI_HARDWARE_PINS.items():
            if all((clock == pins['clock'],
                    mosi in (None, pins['mosi']),
                    miso in (None, pins['miso']),
                    select in pins['select'])):
                device = pins['select'].index(select)
                return (port, device)
            raise CompatibilityException(
                'Invalid pin selection for hardware SPI')
