# -*- coding: utf-8 -*-
"""
py_versions/circuitpython.py

The Circuitpython compatibility file.
"""

import board
from digitalio import DigitalInOut, Direction, Pull
from uasyncio import sleep_ms
from busio import SPI


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

    def __init__(self, mode=None):
        self.__pin_state = {}
        self._sclk = board.SCLK
        self._mosi = board.MOSI
        self._miso = board.MISO

    def pin_mode(self, pin, direction, *, pull=None, default=None, alt=-1):
        """
        Set a pin, direction, pull, mode, and default.

        .. notes::

          See the Circuitython documentation on https://bit.ly/36yPHPl

        @param pin: The pin identifier.
        @type pin: int
        @param direction: The direction IN or OUT based on the board.
        @type direction: int
        @param pull: Sets either a pull up or pull down resistor internal to
                     the board (Pull.UP or Pull.DOWN).
        @type pull: int
        @param default: Set a default value of the pin.
        @type default: int
        @param alt: Not used with Circuitpython.
        @type alt: int
        """
        self.__pin_state[pin] = DigitalInOut(pin)
        self.__pin_state[pin].direction = direction
        if default is not None: pin.value = default

    def digital_write(self, pin, high_low):
        try:
            self.__pin_state[pin].value = high_low
        except KeyError as e:
            print("Error: Pin {} has not been set, {}".format(pin, e))

    def delay(self, ms):
        sleep_ms(ms)

    def spi_start_transaction(self):
        from utils.compatibility import Boards
        freq = Boards.get_frequency()
        self._spi = SPI(self._sclk, self._mosi, self._miso)
        while self._spi.try_lock(): pass
        self._spi.configure(baudrate=freq)
        self._spi.unlock()

    def spi_end_transaction(self):
        self._spi.deinit()

    def spi_write(self, value):
        self.digital_write(self._rs, self.LOW)

        try:
            self.__pin_state[self._cs].value = self.LOW
            self._spi.write(value)
        finally:
            self.__pin_state[self._cs].value = self.HIGH

    def set_spi_ports(self, sclk, mosi, miso):
        """
        Optional call if you want to use a secondary SPI port.

        .. note::

            This method must be called before the begin() method.

        @param sclk: The SPI clock pin.
        @type sclk: int
        @param mosi: Master Out Slave In pin.
        @type mosi: int
        @param miso: Master In Slave Out pin.
        @type: miso: int
        """
        self._sclk = sclk
        self._mosi = mosi
        self._miso = miso
