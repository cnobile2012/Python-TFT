# -*- coding: utf-8 -*-
"""
py_versions/raspberrypi.py

The Raspberry Pi Linux compatibility file.
"""

from RPi import GPIO
from spidev import SpiDev
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

    # To get second port add "dtoverlay=spi1-3cs" to "/boot/config.txt".
    _SPI_HARDWARE_PINS = {
        0: {'clock':  11,
            'mosi':   10,
            'miso':   9,
            'select': (8, 7)},
        1: {'clock':  21,
            'mosi':   20,
            'miso':   19,
            'select': (18, 17, 16)}
        }

    def __init__(self, mode=GPIO.BCM):
        """
        Constructor

        @param mode: The Raspberry PI board mode (GPIO.BOARD or GPIO.BCM).
                     The default is GPIO.BCM.
        @type mode: int
        """
        mode = mode if mode is not None else GPIO.BCM
        GPIO.setmode(mode)

    def pin_mode(self, pin, direction, *, pull=INPUT_PULLOFF, default=None,
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
        """
        Set the given pin either high or low.

        @param pin: The pin to set.
        @type pin: int
        @param high_low: Set HIGH (True) or LOW (False).
        @type high_low: bool
        """
        GPIO.output(pin, high_low)

    def pin_cleanup(self):
        """
        To be run after this API is no longer to be used.
        """
        GPIO.cleanup()

    def delay(self, ms):
        sleep(ms/1000) # Convert to floating point.

    def spi_start_transaction(self, reuse=False):
        if self._spi is None or not reuse:
            from utils.compatibility import Boards, CompatibilityException

            try:
                self._spi = SpiDev()
                port, device = self.spi_port_device(
                    self._clk, self._sdi, None, self._cs)
                self._spi.open(port, device)
                self._spi.max_speed_hz = Boards.get_frequency(self.BOARD)
            except Exception as e:
                self.spi_end_transaction()
                raise CompatibilityException(e)

    def spi_end_transaction(self):
        if self._spi:
            self._spi.close()
            self._spi = None

    def spi_write(self, values, bits_16=True):
        if not isinstance(values, (list, tuple)):
            values = [values]
        elif isinstance(values, tuple):
            values = list(values)

        items = []

        for value in values:
            if bits_16:
                items.append(value >> 8)
                items.append(value & 0xFF)
            else:
                items.append(value)

        self._spi.writebytes(items)
