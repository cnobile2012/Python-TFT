# -*- coding: utf-8 -*-
"""
py_versions/raspberrypi.py

The Raspberry Pi Linux compatibility file.
"""

from RPi import GPIO
from spidev import SpiDev
from time import sleep

from utils.common import Boards, CompatibilityException


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
    _SPI_MODE = 0
    _DEF_PWM_FREQ = 25500

    # To get second port add "dtoverlay=spi1-3cs" to "/boot/config.txt".
    _SPI_HARDWARE_PORTS = {
        # clock = 11, mosi = 10, and miso = 9
        0: (8, 7),
        # clock = 21, mosi = 20, and miso = 19
        1: (18, 17, 16)
        }

    def __init__(self, mode=GPIO.BCM):
        """
        Constructor

        :param mode: The Raspberry PI board mode (GPIO.BOARD or GPIO.BCM).
                     The default is GPIO.BCM.
        :type mode: int
        """
        mode = mode if mode is not None else GPIO.BCM
        GPIO.setmode(mode)
        GPIO.setwarnings(False)
        self._spi = None
        self.__pwm_pin_states = {}

        if self.TESTING:
            self.__write = self._spi.xfer2
            self.__read = self.__test_read
        else:
            self.__write = self._spi.writebytes
            self.__read = self.__dummy_read

    def pin_mode(self, pin, direction, *, pull=INPUT_PULLOFF, default=None):
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
        """
        GPIO.setup(pin, direction, pull_up_down=pull)

        if direction == self.OUTPUT and default is not None:
            GPIO.output(pin, default)

    def digital_write(self, pin, high_low):
        """
        Set the given pin either high or low.

        :param pin: The pin to set.
        :type pin: int
        :param high_low: Set HIGH (True) or LOW (False).
        :type high_low: bool
        """
        GPIO.output(pin, high_low)

    def pin_cleanup(self):
        """
        To be run after this API is no longer to be used.
        """
        for obj in self.__pwm_pin_states.values():
            obj.stop()

        GPIO.cleanup()

    def delay(self, ms):
        """
        Set a delay in milliseconds.

        :param ms: The value in milliseconds.
        :type ms: int
        """
        sleep(ms/1000) # Convert to floating point.

    def _spi_port_device(self):
        """
        Convert a mapping of pin definitions, which must contain 'clock',
        and 'select' at a minimum, for a hardware SPI port.

        :raises CompatibilityException: If the spi port number is invalid for
                                        the current board or the cs pin is
                                        not valid.
        """
        # The port variable is sometimes refered to as the bus.
        try:
            data = self._SPI_HARDWARE_PORTS[self._spi_port]
        except KeyError:
            msg = self.ERROR_MSGS['INV_PORT'].format(
                Boards.get_board_name(self.BOARD))
            raise CompatibilityException(msg)

        if self._cs in data:
            self._device = data.index(self._cs)
        else:
            msg = ("Invalid cs pin '{}' selection for port '{}'."
                   ).format(self._cs, self._spi_port)
            raise CompatibilityException(msg)

    def spi_start_transaction(self):
        """
        Create the SPI connection.

        :raises CompatibilityException: If the spi calls fail.
        """
        if self._spi is None:
            try:
                self._spi = SpiDev()
                self._spi.open(self._spi_port, self._device)
                self._spi.max_speed_hz = self.spi_frequency
                self._spi.mode = self._SPI_MODE
            except IndexError as e: # pragma: no cover
                msg = ("There were no frequencies defines for the {} board, {}"
                       ).format(Boards.get_board_name(self.BOARD), e)
                raise CompatibilityException(msg)
            except Exception as e: # pragma: no cover
                self.spi_end_transaction()
                raise CompatibilityException(e)

    def spi_end_transaction(self):
        """
        Destroy the SPI connection.
        """
        if self._spi is not None:
            self._spi.close()
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
        Write to the SPI port the given values.

        :param values: The values to write.
        :type values: int, list, or tuple
        """
        if not isinstance(values, (list, tuple)):
            values = [values]
        elif isinstance(values, tuple):
            values = list(values)

        items = []

        for value in values:
            value = round(value)
            items.append(value >> 8)
            items.append(value & 0xFF)

        try:
            self.__write(items)
        except Exception as e: # pragma: no cover
            raise CompatibilityException("Error writing: {}".format(str(e)))
        else:
            self.__read(result)

    def __dummy_read(self, result):
        pass

    def __test_read(self, result):
        data = []

        for idx in range(0, len(result), 2):
            high, low = result[idx: idx + 2]
            data.append((high << 8) | low)

        return data

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
        self.__pwm_pin_states[pin] = GPIO.PWM(pin, self.pwm_frequency)
        self.__pwm_pin_states[pin].start(duty_cycle)

    def change_led_duty_cycle(self, brightness):
        """
        Writes the value to the analog PWM pin.

        :param pin: The pin to setup the PWM on.
        :type pin: int
        :param brightness: The brightness value.
        :type value: int
        """
        duty_cycle = self.__get_duty_cycle(brightness)
        self.__pwm_pin_states[self._led].ChangeDutyCycle(duty_cycle)

    def __get_duty_cycle(self, brightness):
        return (brightness * 100 // (self.MAX_BRIGHTNESS + 1)
                if brightness != 0 else 0)
