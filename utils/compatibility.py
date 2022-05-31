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


class _Boards:
    _BOARD_SPECS = (
        ('ARDUINO_STM32_FEATHER', (42000000, 21000000)),
        ('ARDUINO_ARCH_STM32', (16000000,)),
        ('ARDUINO_ARCH_STM32F1', (18000000,)),
        ('STM32F1', (0,)),
        ('ARDUINO_FEATHER52', (0,)),
        ('TEENSYDUINO', (8000000,)),
        ('ESP8266', (40000000,)),
        ('ESP32', (40000000,)),
        ('RASPI', (31200000,)),
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
        return board_spec[0] if board_spec is not None else None

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
    def get_frequencies(board_id):
        """
        Get a tuple of frequencies where each frequency relates to a
        spacific port on the board.

        :param board_id: The numerical board ID.
        :type board_id: int
        :return: A tuple of frequencies.
        :rtype: tuple
        """
        board_spec = Boards._BOARDS.get(board_id)
        return board_spec[1] if board_spec is not None else ()

Boards = _Boards()


class Compatibility(PiVersion):
    """
    Checks the compatibility and version of Python.
    """

    def __init__(self, mode=None):
        if not None:
            super().__init__(mode)

        self.BOARD = None

    def _get_board_name(self, board_id=None):
        board_id = 1000 if board_id is None and self.BOARD is None else board_id
        board_id = board_id if board_id is not None else self.BOARD
        return Boards.get_board_name(board_id)

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
