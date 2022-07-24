# -*- coding: utf-8 -*-
"""
utils/compatibility.py

This class defines a generic compatibility class to normalize between
different versions of Python. i.e. C standard, MicroPython, and CircuitPython

We need to test for the existence of a few methods and functions then decide
which to use in this library.
"""

from .common import Boards, CompatibilityException


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


class Compatibility(PiVersion):
    """
    Checks the compatibility and version of Python.
    """

    def __init__(self, rpi_mode=None):
        if not None:
            super().__init__(rpi_mode)

        # _DEF_PWM_FREQ will be different for all the Python versions.
        self.__pwm_freq = self._DEF_PWM_FREQ
        self.__spi_freq = 0
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
        board_name = self._get_board_name(board)

        if board_name not in [v for v in dir(Boards) if not v.startswith('_')]:
            raise CompatibilityException(
                self.ERROR_MSGS['BRD_UNSUP'].format(board_name))

        self.BOARD = board

    @property
    def pwm_frequency(self):
        """
        Get the current PWM frequency.

        :return: The current PWM frequency.
        :rtype: int
        """
        return self.__pwm_freq

    @pwm_frequency.setter
    def pwm_frequency(self, freq):
        """
        Set the PWM frequency.

        .. note::

          The PWM frequency if the default needs to be superseded must
          be set before begin() is called.

        :param freq: The PWM frequency.
        :type freq: int
        """
        self.__pwm_freq = freq

    @property
    def spi_frequency(self):
        """
        Get the current SPI frequency.

        :return: The current SPI frequency.
        :rtype: int
        """
        if self.__spi_freq == 0:
            if self.BOARD in (Boards.ESP8266, Boards.ESP32):
                idx = self._spi_port - 1
            else:
                idx = self._spi_port

            try:
                freq = Boards.get_frequency(self.BOARD, idx)
            except IndexError as e:
                board_name = Boards.get_board_name(self.BOARD)
                raise CompatibilityException(
                    self.ERROR_MSGS['INV_PORT'].format(board_name))
        else:
            freq = self.__spi_freq

        return freq

    @spi_frequency.setter
    def spi_frequency(self, freq):
        """
        Set the SPI frequency.

        .. note::

          The SPI frequency if the default needs to be superseded must
          be set before begin() is called.

        :param freq: The SPI frequency.
        :type freq: int
        """
        self.__spi_freq = freq

    def set_spi_pins(self, sck, mosi, miso=-1):
        """
        Set the SPI pins.

        Optional call if you want to change the SPI pins. The proper GPIO
        pins are generally used not the actual pins on your board.

        .. note::

          1. If using CircuitPython this method is required.
          2. This method must be called before the begin() method.

        :param sck: The SPI clock pin.
        :type sck: int
        :param mosi: Master Out Slave In pin.
        :type mosi: int
        :param miso: Master In Slave Out pin.
        :type: miso: int
        """
        self._sck = sck
        self._mosi = mosi
        self._miso = miso
