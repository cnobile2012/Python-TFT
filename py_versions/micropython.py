# -*- coding: utf-8 -*-
"""
py_versions/micropython.py

The Micropython compatibility file.
"""

from machine import SPI, Pin
from time import sleep_ms


class PiVersion:
    """
    This class implements the Micropython version of the low level
    functionality.
    """
    PLATFORM = "MicroPython"
    HIGH = True
    LOW = False
    INPUT = Pin.IN
    OUTPUT = Pin.OUT
    INPUT_PULLUP = Pin.PULL_UP
    INPUT_PULLDOWN = Pin.PULL_DOWN
    INPUT_PULLOFF = None

    def __init__(self, mode=None):
        self.__pin_state = {}
        self._sclk = None
        self._mosi = None
        self._miso = None
        self._port = 0

    def pin_mode(self, pin, direction, *, pull=-1, default=None, alt=-1):
        """
        Set a pin, direction, pull, mode, and default.

        .. notes::

          See the Micropython documentation on https://bit.ly/33WltF3

        :param pin: The pin identifier.
        :type pin: int
        :param direction: The direction IN or OUT based on the board.
        :type direction: int
        :param pull: Sets either a pull up or pull down resistor internal to
                     the board (Pin.PULL_UP or Pin.PULL_DOWN).
        :type pull: int
        :param default: Set a default value of the pin.
        :type default: int
        :param alt: Specifies an alternate function for the pin method.
        :type alt: int
        """
        self.__pin_state[pin] = Pin(pin, direction, pull,
                                    value=default, alt=alt)

    def digital_write(self, pin, high_low):
        """
        Set the given pin either high or low.

        :param pin: The pin to set.
        :type pin: int
        :param high_low: Set HIGH (True) or LOW (False).
        :type high_low: bool
        """
        self.__pin_state[pin].value(high_low)

    def delay(self, ms):
        sleep_ms(ms)

    def spi_start_transaction(self, reuse=False):
        if self._spi is None or not reuse:
            from utils.compatibility import Boards
            self._spi = SPI(self._port, baudrate=Boards.get_frequency())

    def spi_end_transaction(self):
        self._spi.deinit()

    def spi_write(self, value):
        """
        Write data to the SPI port. First set the rs pin to command mode
        then the cs (chip select) pin to low (selected) then write the data
        then set the cs pin to high (unselected).

        .. note::

          This method can raise the KeyError exception if the pin_mode()
          method was not called first on the pins used in this method.

        :param value: The value to write to the SPI port.
        :type value: str
        """
        self.__pin_state[self._rs].low()

        try:
            self.__pin_state[self._cs].low()
            self._spi.write(value)
        finally:
            self.__pin_state[self._cs].high()

    def set_spi_port(self, port=0):
        """
        This sets the ports to use assuming the board has multiple SPI ports.
        MicroPython refers to the as the id.

        :param port: Value 0, 1 etc. Depends on the MCU and board used.
                     Defaults is 0.
        :type port: int
        """
        self._port = port
