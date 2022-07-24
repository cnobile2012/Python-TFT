# -*- coding: utf-8 -*-
"""
py_versions/circuitpython.py

The CircuitPython compatibility file.
"""

import board
from digitalio import DigitalInOut, Direction, Pull
from uasyncio import sleep_ms
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
    INPUT = Direction.IN
    OUTPUT = Direction.OUT
    INPUT_PULLUP = Pull.UP
    INPUT_PULLDOWN = Pull.DOWN
    INPUT_PULLOFF = None
    _DEF_PWM_FREQ = 102400
    _GP_PINS = [pin for pin in dir(board) if not pin.startswith('_')]

    def __init__(self, mode=None):
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

    def pin_cleanup(self):
        """
        To be run after this API is no longer used.
        """
        for obj in self.__pwm_pin_states.values():
            obj.deinit()

    def delay(self, ms):
        sleep_ms(ms)

    def _spi_port_device(self):
        """
        We just need to test that the SCK and MOSI pins have been set.
        """
        if (-1 in (self._sck, self._mosi) or self._sck not in self._GP_PINS
            or self._mosi not in self._GP_PINS):
            msg = ("At a minimum SCK '{}' and MOSI '{}' needs to be "
                   "set to a GPIO pin.")
            raise CompatibilityException(msg.format(self._sck, self._mosi))

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

    def spi_write(self, values):
        """
        Write data to the SPI port. First set the rs pin to command mode
        then the cs (chip select) pin to low (selected) then write the data
        then set the cs pin to high (unselected).

        :param value: The value to write to the SPI port.
        :type value: str
        """
        if not isinstance(values, (list, tuple)):
            values = [values]
        elif isinstance(values, tuple):
            values = list(values)

        items = bytearray()

        for value in values:
            value = round(value)
            items.append(value >> 8)
            items.append(value & 0xFF)

        try:
            self._spi.write(items)
        except Exception as e:
            raise CompatibilityException("Error writing: {}".format(str(e)))

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
        self.__pwm_pin_states[pin] = PWMOut(
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
        self.__pwm_pin_states[self._led].duty_cycle = duty_cycle

    def __get_duty_cycle(self, brightness):
        duty_cycle = 0

        if brightness == self.MAX_BRIGHTNESS:
            duty_cycle = 0xffff
        elif brightness > 0:
            duty_cycle = brightness * 0xffff // (self.MAX_BRIGHTNESS + 1)

        return duty_cycle
