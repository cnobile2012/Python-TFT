#!/usr/bin/env python3
#
# Test the SPIDev API.
#
# Test conditions:
#   1. Connect the MISO pin to the MOSI pin.
#   2. If testing port 1 (default is 0) then `dtoverlay=spi1-3cs` must be
#      in the `/boot/config.txt` file on the RPI.
#

import os
import sys
from RPi import GPIO
from spidev import SpiDev

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_PATH)

from ILI9225 import CompatibilityException


class SPITest(SpiDev):
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
    FREQ = 35000000
    SPI_MODE = 0

    def __init__(self, miso=9, mosi=10, clock=11, select=8, speed=31200000,
                 mode=GPIO.BCM):
        self._miso = miso
        self._mosi = mosi
        self._clock = clock
        self._select = select
        self._speed = speed
        self._spi = None
        mode = mode if mode is not None else GPIO.BCM
        GPIO.setmode(mode)
        GPIO.setwarnings(False)

    def begin(self):
        # Control pins
        self.pin_mode(self._select, GPIO.OUT)
        self.digital_write(self._select, GPIO.HIGH)

    def pin_mode(self, pin, direction, *, pull=GPIO.PUD_OFF, default=None,
                 alt=-1):
        """
        Set a pin, direction, pull, mode, and default.

        :param pin: The pin identifier.
        :type pin: int
        :param direction: The direction IN or OUT based on the board.
        :type direction: int
        :param pull: Sets either a pull up or pull down resistor internal to
                     the RPi (GPIO.PUD_UP, GPIO.PUD_DOWN, or GPIO.PUD_OFF).
        :type pull: int
        :param default: Set a default value of the pin.
        :type default: int
        :param alt: Not used on the RPi.
        :type alt: int
        """
        GPIO.setup(pin, direction, pull_up_down=pull)
        if default is not None: GPIO.output(pin, default)

    def digital_write(self, pin, high_low):
        """
        Set the given pin either high or low.

        :param pin: The pin to set.
        :type pin: int
        :param high_low: Set HIGH (True) or LOW (False).
        :type high_low: bool
        """
        GPIO.output(pin, high_low)

    def spi_start_transaction(self):
        try:
            self._spi = SpiDev()
            port, device = self.spi_port_device(
                self._clock, self._mosi, self._miso, self._select)
            self._spi.open(port, device)
            self._spi.max_speed_hz = self._speed
            self._spi.mode = self.SPI_MODE
        except Exception as e:
            self.spi_end_transaction()
            raise e

    def spi_end_transaction(self):
        if self._spi:
            self._spi.close()
            self._spi = None

    def spi_write(self, values):
        ## if not isinstance(values, (list, tuple)):
        ##     values = [values]
        ## elif isinstance(values, tuple):
        ##     values = list(values)

        ## result = None
        ## items = []

        ## for value in values:
        ##     items.append(value >> 8)
        ##     items.append(value & 0xFF)

        ## print(f"Items: {items}")
        print(f"values: {values}")
        self.digital_write(self._select, GPIO.LOW)
        result = None

        try:
            result = self._spi.xfer2(values)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.digital_write(self._select, GPIO.HIGH)
            if result: print(f"Result: {result}")

    def spi_port_device(self, clock, mosi, miso, select):
        """
        Convert a mapping of pin definitions, which must contain 'clock',
        and 'select' at a minimum, to a hardware SPI port, device tuple.

        :param clock: The SPI clock pin number.
        :type clock: int
        :param mosi: The SPI -- Master Output Slave Input pin number.
        :type mosi: int
        :param miso: The SPI -- Master Input Slave Output pin number.
        :type miso: int
        :param select: The SPI Chip Select pin number.
        :type select: int
        :returns: A tuple of (port, device).
        :rtype: tuple
        :raises CompatibilityException: If the pins do not represent a valid
                                        hardware SPI device.
        """
        # The port variable is sometimes refered to as the bus.
        for port, pins in self._SPI_HARDWARE_PINS.items():
            if all((clock == pins['clock'],
                    mosi in (None, pins['mosi']),
                    miso in (None, pins['miso']),
                    select in pins['select'])):
                device = pins['select'].index(select)
                print(f"Using -- port: {port}, device: {device}")
                return (port, device)

        raise CompatibilityException('Invalid pin selection for hardware SPI')


if __name__ == '__main__':
    st = SPITest()
    st.begin()
    st.spi_start_transaction()
    values = (0x10, 0xFF, 0x10FF)
    array = bytearray()

    for value in values:
        array.append(value >> 8)
        array.append(value & 0xFF)

    st.spi_write(array)
    st.spi_end_transaction()
