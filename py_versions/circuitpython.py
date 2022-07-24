# -*- coding: utf-8 -*-
"""
py_versions/circuitpython.py

The CircuitPython compatibility file.
"""

import board
from digitalio import DigitalInOut, Direction, Pull
from uasyncio import sleep_ms
from busio import SPI

from utils.common import Boards, CompatibilityException


class PiVersion:
    """
    This class implements the Raspberry Pi version of the low level
    functionality.
    """
    PLATFORM = "CircuitPython"
    HIGH = True
    LOW = False
    INPUT = Direction.IN
    OUTPUT = Direction.OUT
    INPUT_PULLUP = Pull.UP
    INPUT_PULLDOWN = Pull.DOWN
    INPUT_PULLOFF = None
    _DEF_PWM_FREQ = 102400

    def __init__(self, mode=None):
        self.__pin_state = {}
        self._sclk = board.SCLK
        self._mosi = board.MOSI
        self._miso = board.MISO

    def pin_mode(self, pin, direction, *, pull=None, default=None):
        """
        Set a pin, direction, pull, mode, and default.

        .. note::

          See the CircuitPython documentation on https://bit.ly/36yPHPl

        :param pin: The pin identifier.
        :type pin: int
        :param direction: The direction IN or OUT based on the board.
        :type direction: int
        :param pull: Sets either a pull up or pull down resistor internal
                     to the board (Pull.UP or Pull.DOWN).
        :type pull: int
        :param default: Set a default value of the pin.
        :type default: int
        """
        self.__pin_state[pin] = DigitalInOut(pin)
        self.__pin_state[pin].direction = direction
        if default is not None: pin.value = default

    def digital_write(self, pin, high_low):
        """
        Set the given pin either high or low.

        :param pin: The pin to set.
        :type pin: int
        :param high_low: Set HIGH (True) or LOW (False).
        :type high_low: bool
        """
        self.__pin_state[pin].value = high_low

    def delay(self, ms):
        sleep_ms(ms)

    def _spi_port_device(self):
        """
        We just need to test that the GPIO pins have been set.
        """


        pass

    def spi_start_transaction(self):
        if self._spi is None:
            self._spi = SPI(self._sck, self._mosi, self._miso)
            while self._spi.try_lock(): pass
            self._spi.configure(baudrate=Boards.get_frequency())
            self._spi.unlock()

    def spi_end_transaction(self):
        """
        Destroy the SPI connection.
        """
        if self._spi is not None:
            self._spi.deinit()
            self._spi = None

    @property
    def is_spi_connected(self):
        """
        Check if the SPI connection has been established.

        :return: True if connected else False
        :rtype: bool
        """
        return True if self._spi is not None else False

    def spi_write(self, value):
        self.__pin_state[self._rs].value = self.LOW

        try:
            self.__pin_state[self._cs].value = self.LOW
            self._spi.write(value)
        finally:
            self.__pin_state[self._cs].value = self.HIGH
