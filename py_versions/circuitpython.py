# -*- coding: utf-8 -*-
"""
py_versions/circuitpython.py

The CircuitPython compatibility file.
"""

import board
from digitalio import DigitalInOut, Direction, Pull
from time import sleep
from busio import SPI
from pwmio import PWMOut

from utils.common import Boards, CompatibilityException


class PiVersion:
    """
    This class implements the Raspberry Pi version of the low level
    functionality.
    """
    PLATFORM = "CircuitPython"
    HIGH = True
    LOW = False
    INPUT = Direction.INPUT
    OUTPUT = Direction.OUTPUT
    INPUT_PULLUP = Pull.UP
    INPUT_PULLDOWN = Pull.DOWN
    INPUT_PULLOFF = None
    _DEF_PWM_FREQ = 102400
    _GP_PINS = ["board.{}".format(pin) for pin in dir(board)
                if not pin.startswith('_')]
    BYTEARRAY_SIZE = 4092

    def __init__(self, mode=None):
        self._spi = None
        self.__pin_state = {}
        self.__pwm_pin_states = {}

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
        self.__pin_state[str(pin)] = DigitalInOut(pin)
        self.__pin_state[str(pin)].direction = direction
        if default is not None: self.__pin_state[str(pin)].value = default

    def digital_write(self, pin, high_low):
        """
        Set the given pin either high or low.

        :param pin: The pin to set.
        :type pin: int
        :param high_low: Set HIGH (True) or LOW (False).
        :type high_low: bool
        """
        self.__pin_state[str(pin)].value = high_low

    def pin_cleanup(self):
        """
        To be run after this API is no longer used.
        """
        if self._spi: self._spi.deinit()

        for obj in self.__pin_state.values():
            obj.deinit()

        for obj in self.__pwm_pin_states.values():
            obj.deinit()

    def delay(self, ms):
        """
        Set a delay in milliseconds.

        :param ms: The value in milliseconds.
        :type ms: int
        """
        sleep(ms/1000) # Convert to floating point.

    def _spi_port_device(self):
        """
        We just need to test that the SCK and MOSI pins have been set.
        """
        if (-1 in (self._sck, self._mosi)
            or str(self._sck) not in self._GP_PINS
            or str(self._mosi) not in self._GP_PINS):
            msg = ("At a minimum SCK '{}' and MOSI '{}' needs to be "
                   "set to a GPIO pin, your options are: {}")
            raise CompatibilityException(msg.format(
                self._sck, self._mosi, self._GP_PINS))

    def spi_start_transaction(self):
        if self._spi is None:
            if self._miso == -1:
                miso = None
            else:
                miso = self._miso

            self._spi = SPI(self._sck, self._mosi, miso)
            while self._spi.try_lock(): pass
            self._spi.configure(baudrate=self.spi_frequency)
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

    def spi_write(self, values):
        """
        Write data to the SPI port. First set the rs pin to command mode
        then the cs (chip select) pin to low (selected) then write the data
        then set the cs pin to high (unselected).

        :param value: The value to write to the SPI port.
        :type value: str or bytearray
        """
        if not isinstance(values, bytearray):
            items = values

            if isinstance(items, (int, float)):
                items = round(items)
                items = [items]

            values = bytearray()

            for item in items:
                values.append(item >> 8)
                values.append(item & 0xFF)

        self.digital_write(self._cs, self.LOW)

        try:
            while self._spi.try_lock(): pass
            self._spi.write(values)
        except Exception as e:
            raise CompatibilityException("Error writing: {}".format(str(e)))
        finally:
            self._spi.unlock()
            self.digital_write(self._cs, self.HIGH)

    def _need_chunking(self, array):
        array_len = len(array)
        return (array_len >= self.BYTEARRAY_SIZE
                or array_len == (self.BYTEARRAY_SIZE -1))

    def setup_pwm(self, pin, brightness):
        """
        Setup a PWM for controlling the back light LEDs brightness.

        .. note::

          The duty_cycle is derived by multiplying the brightness by 100
          then dividing by the maximum number of brightness values.

        :param pin: The pin to setup the PWM on.
        :type pin: int
        :param brightness: Sets the duty cycle.
        :type brightness: int
        """
        duty_cycle = self.__get_duty_cycle(brightness)
        self.__pwm_pin_states[str(pin)] = PWMOut(
            self._led, duty_cycle=duty_cycle, frequency=self._DEF_PWM_FREQ)

    def change_led_duty_cycle(self, brightness):
        """
        Writes the value to the analog PWM pin.

        :param pin: The pin to setup the PWM on.
        :type pin: int
        :param brightness: The brightness value.
        :type value: int
        """
        duty_cycle = self.__get_duty_cycle(brightness)
        self.__pwm_pin_states[str(self._led)].duty_cycle = duty_cycle

    def __get_duty_cycle(self, brightness):
        duty_cycle = 0

        if brightness == self.MAX_BRIGHTNESS:
            duty_cycle = 0xffff
        elif brightness > 0:
            duty_cycle = brightness * 0xffff // (self.MAX_BRIGHTNESS + 1)

        return duty_cycle
