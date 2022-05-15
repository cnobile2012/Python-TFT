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
    __FREQ = 25500

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

        :param mode: The Raspberry PI board mode (GPIO.BOARD or GPIO.BCM).
                     The default is GPIO.BCM.
        :type mode: int
        """
        mode = mode if mode is not None else GPIO.BCM
        GPIO.setmode(mode)
        GPIO.setwarnings(False)
        self.__pwm_pin_states = {}

    def pin_mode(self, pin, direction, *, pull=INPUT_PULLOFF, default=None,
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
        Set a delat in milliseconds.

        :param ms: The value in milliseconds.
        :type ms: int
        """
        sleep(ms/1000) # Convert to floating point.

    def spi_start_transaction(self):
        """
        Create the SPI connection.
        """
        if self._spi is None:
            from utils import Boards, CompatibilityException

            try:
                self._spi = SpiDev()
                port, device = self.spi_port_device(
                    self._clk, self._sdi, None, self._cs)
                self._spi.open(port, device)
                self._spi.max_speed_hz = Boards.get_frequency(self.BOARD)
                self._spi.mode = self._SPI_MODE
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

    def is_spi_connected(self):
        """
        Check if the SPI connection is established.

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
        from utils import CompatibilityException

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
            if self.TESTING:
                from utils import Boards

                if self.BOARD == Boards.RASPI:
                    result = self._spi.xfer2(items)
            else: # pragma: no cover
                self._spi.writebytes(items)
        except Exception as e:
            raise CompatibilityException("Error writing: {}".format(str(e)))
        else:
            if self.TESTING and self.BOARD == Boards.RASPI:
                high, low = result
                return hex((high << 8) | low)

    def setup_pwm(self, pin, brightness):
        """
        Setup a PWM for controlling the back light LEDs brightness.

        .. notes::

          The duty_cycle is derived by multiplying the brightness by 100
          then  dividing by the maximum number of brightness values.

        :param pin: The pin to setup the PWM on.
        :type pin: int
        :param brightness: Sets the duty cycle.
        :type brightness: int
        """
        duty_cycle = (brightness * 100 / (self._tft.MAX_BRIGHTNESS + 1)
                      if brightness != 0 else 0)
        self.__pwm_pin_states[pin] = GPIO.PWM(pin, self.__FREQ)
        self.__pwm_pin_states[pin].start(duty_cycle)

    def change_duty_cycle(self, pin, brightness):
        """
        Writes the value to the analog PWM pin.

        :param pin: The pin to setup the PWM on.
        :type pin: int
        :param brightness: The brightness value.
        :type value: int
        """
        duty_cycle = (brightness * 100 / (self._tft.MAX_BRIGHTNESS + 1)
                      if brightness != 0 else 0)
        self.__pwm_pin_states[pin].ChangeDutyCycle(duty_cycle)
