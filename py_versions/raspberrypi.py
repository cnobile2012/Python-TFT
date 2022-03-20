# -*- coding: utf-8 -*-
"""
py_versions/raspberrypi.py

The Raspberry Pi Linux compatibility file.
"""

from gpiozero import SPIDevice
from time import sleep


class PiVersion:
    """
    This class implements the Raspberry Pi version of the low level
    functionality.
    """
    PLATFORM = "Raspberry Pi"
    HIGH = GPIO.HIGH
    LOW = GPIO.LOW
    INPUT = GPIO.IN
    OUTPUT = GPIO.OUT
    INPUT_PULLUP = GPIO.PUD_UP
    INPUT_PULLDOWN = GPIO.PUD_DOWN
    INPUT_PULLOFF = GPIO.PUD_OFF

    def __init__(self, mode=GPIO.BCM):
        """
        Constructor

        @param mode: The Raspberry PI board mode (GPIO.BOARD or GPIO.BCM).
                     The default is GPIO.BCM.
        @type mode: int
        """
        mode = mode if mode is not None else GPIO.BCM
        GPIO.setmode(mode)
        self._port = 0

    def pin_mode(self, pin, direction, *, pull=GPIO.PUD_OFF, default=None,
                 alt=-1):
        """
        Set a pin, direction, pull, mode, and default.

        @param pin: The pin identifier.
        @type pin: int
        @param direction: The direction IN or OUT based on the board.
        @type direction: int
        @param pull: Sets either a pull up or pull down resistor internal to
                     the RPi (GPIO.PUD_UP, GPIO.PUD_DOWN, or GPIO.PUD_OFF).
        @type pull: int
        @param default: Set a default value of the pin.
        @type default: int
        @param alt: Not used on the RPi.
        @type alt: int
        """
        GPIO.setup(pin, direction, pull_up_down=pull)
        if default is not None: GPIO.output(pin, default)

    def digital_write(self, pin, high_low):
        GPIO.output(pin, high_low)

    def delay(self, ms):
        sleep(ms/1000) # Convert to floating point.


    def spi_start_transaction(self):
        self._spi = SPIDevice(port=self._port)

    def spi_end_transaction(self):
        self._spi.close()

    def spi_write(self, value):
        ## self.digital_write(self._rs, self.LOW)

        ## try:
        ##     self.__pin_state[self._cs].low()
        ##     self._spi.write(value)
        ## finally:
        ##     self.__pin_state[self._cs].high()
        pass

    def set_spi_port(self, port=0):
        """
        This sets the ports to use assuming the board has multiple SPI ports.

        .. note::

          There are two SPI ports on the Raspberry Pi port = 0
          SPI0: MOSI (GPIO10); MISO (GPIO9); SCLK (GPIO11); CE0 (GPIO8);
          CE1 (GPIO7)
          and port = 1
          SPI1: MOSI (GPIO20); MISO (GPIO19); SCLK (GPIO21); CE0 (GPIO18);
          CE1 (GPIO17); CE2 (GPIO16)

        @param port: Value 0, 1 etc. Depends on the version of the
                     Raspberry Pi. Defaults is 0.
        @type port: int
        """
        self._port = port
