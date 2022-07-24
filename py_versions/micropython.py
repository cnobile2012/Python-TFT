# -*- coding: utf-8 -*-
"""
py_versions/micropython.py

The MicroPython compatibility file.

CC32xx   = port 0=SPI1 (MISO=GPIO15, MOSI=GPIO16, CLK=GPIO14, CS=GPIO17)
ESP8266  = port 1=HSPI (MISO=GPIO12, MOSI=GPIO13, SCK=GPIO14, CS0=GPIO15)
ESP32    = port 1=HSPI (MISO=GPIO12, MOSI=GPIO13, SCK=GPIO14, CS0=GPIO15)
         = port 2=VSPI (MISO=GPIO19, MOSI=GPIO23, SCK=GPIO18, CS0=GPIO5)
NRF52    = port 0=SPIM0 (All pins are configurable)
         = port 1=SPIM1 (All pins are configurable)
         = port 2=SPIM2 (All pins are configurable)
         = port 3=SPIM3 (All pins are configurable)
RP2040   = port 0=SPI0 (MISO=GPIO4, MOSI=GPIO7, SCK=GPIO6)
         = port 1=SPI1 (MISO=GPIO8, MOSI=GPIO11, SCK=GPIO10)
STM32F0  = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5)
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
         = port 2=SPI2 (MISO=PB14, MOSI=PB15, SCK=PB13)
STM32F1  = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
         = port 2=SPI2 (MISO=PB13, MOSI=PB14, SCK=PB12) or
                       (MISO=PB14, MOSI=PB15, SCK=PB13)
         = port 3=SPI3 (MISO=PB4, MOSI=PB5, SCK=PB3)
STM32F2  = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
         = port 2=SPI2 (MISO=PC2, MOSI=PC3, SCK=PB10) or
                       (MISO=PC14, MOSI=PC15, SCK=PB13) or
                       (MISO=PI2, MOSI=PI3, SCK=PI1)
         = port 3=SPI3 (MISO=PC11, MOSI=PC12, SCK=PC10) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
STM32F3  = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
         = port 2=SPI2 (MISO=PB14, MOSI=PB15, SCK=PB13) (SCK=PF9, SCK=PF10)
         = port 3=SPI3 (MISO=PC11, MOSI=PC12, SCK=PC10)
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
STM32F4  = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5)
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
         = port 2=SPI2 (MISO=PC2, MOSI=PC3, SCK=PB10) or
                       (MISO=PB14, MOSI=PB15, SCK=PB13) or
                       (MISO=PI2, MOSI=PI3, SCK=PI1)
         = port 3=SPI3 (MISO=PC11, MOSI=PC12, SCK=PC10) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
STM32F72 = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
           port 2=SPI2 (MISO=PC2, MOSI=PC3, SCK=PC1) (SCK=PD3) or
                       (MISO=PB14, MOSI=PB15, SCK=PB13) (SCK=PB10)
                       (MISO=PI2, MOSI=PI3, SCK=PI1) (SCK=PA9)
           port 3=SPI3 (MISO=PC11, MOSI=PC12, SCK=PC10) (MOSI=PB2, MOSI=PD6)
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
           port 4=SPI4 (MISO=PE5, MOSI=PE6, SCK=PE2)
                       (MISO=PE13, MOSI=PE14, SCK=PE12)
           port 5=SPI5 (MISO=PF8, MOSI=PF9, SCK=PF7)
                       (MISO=PH7, MOSI=PF11, SCK=PH6)
STM32F76 = port 1=SPI1 (MISO=PA6, MOSI=PA7, SCK=PA5) or
                       (MISO=PG9, MOSI=PD7, SCK=PG11) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
           port 2=SPI2 (MISO=PC2, MOSI=PC3, SCK=PB10) (MOSI=PC1) or
                       (MISO=PB14, MOSI=PB15, SCK=PB13) (SCK=PA9, SCK=PA12) or
                       (MISO=PI2, MOSI=PI3, SCK=PI1)
           port 3=SPI3 (MISO=PC11, MOSI=PC12, SCK=PC10) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3) (MOSI=PB2, MOSI=PD6)
           port 4=SPI4 (MISO=PE5, MOSI=PE6, SCK=PE2) or
                       (MISO=PE13, MOSI=PE14, SCK=PE12)
           port 5=SPI5 (MISO=PF8, MOSI=PF9, SCK=PF7) or
                       (MISO=PH7, MOSI=PF11, SCK=PH6)
           port 5=SPI6 (MISO=PA6, MOSI=PA7, SCK=PA5) or
                       (MISO=PG12, MOSI=PG14, SCK=PG13) or
                       (MISO=PB4, MOSI=PB5, SCK=PB3)
"""

from machine import Pin, SPI, PWM, reset
from time import sleep_ms

from utils.common import Boards, CompatibilityException


class PiVersion:
    """
    This class implements the Micropython version of the low level
    TFT functionality.
    """
    PLATFORM = "MicroPython"
    HIGH = True
    LOW = False
    INPUT = Pin.IN
    OUTPUT = Pin.OUT
    INPUT_PULLUP = Pin.PULL_UP
    INPUT_PULLDOWN = Pin.PULL_DOWN
    INPUT_PULLOFF = None
    _DEF_PWM_FREQ = 102400

    # To get second port add "dtoverlay=spi1-3cs" to "/boot/config.txt".
    _SPI_HARDWARE_PORTS = {
        #   SCK, MISO, MOSI, CS0
        Boards.ESP8266: {
            1: (14, 12, 13, 15),
            2: (18, 19, 23, 5)
            },
        Boards.ESP32: {
            1: (14, 12, 13, 15),
            2: (18, 19, 23, 5)
            },
        }

    def __init__(self, mode=None):
        self._spi = None
        self.__pin_state = {}
        self.__pwm_pin_states = {}

    def pin_mode(self, pin, direction=-1, pull=-1, *, default=None):
        """
        Set a pin, direction, pull, mode, and default.

        .. note::

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
        :raises CompatibilityException: If the pin cannot be set.
        """
        try:
            self.__pin_state[pin] = Pin(pin, direction, pull, value=default)
        except Exception as e:
            msg = "Pin {}--direction={}, pull={}, value={}, {}".format(
                pin, direction, pull, default, e)
            raise CompatibilityException(msg)

    def digital_write(self, pin, high_low):
        """
        Set the given pin either high or low.

        :param pin: The pin to set.
        :type pin: int
        :param high_low: Set HIGH (True) or LOW (False).
        :type high_low: bool
        """
        self.__pin_state[pin].value(high_low)

    def pin_cleanup(self):
        """
        To be run after this API is no longer used.
        """
        for obj in self.__pwm_pin_states.values():
            obj.deinit()

        reset()

    def delay(self, ms):
        """
        Set a delay in milliseconds.

        :param ms: The value in milliseconds.
        :type ms: int
        """
        sleep_ms(ms)

    def _spi_port_device(self):
        """
        Convert a mapping of pin definitions, which must contain 'clock',
        and 'select' at a minimum for a hardware SPI port.

        :raises CompatibilityException: If the spi port number is invalid for
                                        the current board.
        """
        try:
            data = self._SPI_HARDWARE_PORTS[self.BOARD][self._spi_port]
        except KeyError:
            msg = self.ERROR_MSGS['INV_PORT'].format(
                Boards.get_board_name(self.BOARD))
            raise CompatibilityException(msg)

        self._sck, self._miso, self._mosi, self._cs = data
        [self.pin_mode(pin) for pin in (self._sck, self._mosi, self._miso)
         if pin != -1]

    def spi_start_transaction(self):
        """
        Create the SPI connection.

        :raises CompatibilityException: If the spi calls fail.
        """
        if self._spi is None:
            kwargs = {}
            kwargs['baudrate'] = self.spi_frequency
            kwargs['polarity'] = 0
            kwargs['phase'] = 0
            kwargs['bits'] = 8
            kwargs['firstbit'] = SPI.MSB
            kwargs['sck'] = self.__pin_state[self._sck]
            kwargs['mosi'] = self.__pin_state[self._mosi]

            if self._miso != -1:
                kwargs['miso'] = self.__pin_state[self._miso]

            try:
                self._spi = SPI(self._spi_port, **kwargs)
            except Exception as e:
                self.spi_end_transaction()
                raise CompatibilityException(e)

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

        .. note::

          This method can raise the KeyError exception if the pin_mode()
          method was not called first on the pins used in this method.

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
        obj = self.__pin_state.setdefault(pin, self.pin_mode(pin, self.OUTPUT))
        duty_cycle = self.__get_duty_cycle(brightness)
        self.__pwm_pin_states[pin] = PWM(obj)
        self.__pwm_pin_states[pin].freq(self._DEF_PWM_FREQ)
        self.__pwm_pin_states[pin].duty(duty_cycle)

    def change_led_duty_cycle(self, brightness):
        """
        Writes the value to the analog PWM pin.

        :param pin: The pin to setup the PWM on.
        :type pin: int
        :param brightness: The brightness value.
        :type value: int
        """
        duty_cycle = self.__get_duty_cycle(brightness)
        self.__pwm_pin_states[self.__pin_state[self._led]].duty(duty_cycle)

    def __get_duty_cycle(self, brightness):
        duty_cycle = 0

        if brightness == self.MAX_BRIGHTNESS:
            duty_cycle = 1023
        elif brightness > 0:
            duty_cycle = brightness * 1024 // (self.MAX_BRIGHTNESS + 1)

        return duty_cycle

        # THIS NEEDS TO BE IN THE MicroPython AND CircuitPythin FILES.
        # Setup SPI clock and data inputs.
        ## if self.BOARD not in (Boards.RASPI,): # pragma: no cover
        ##     self.pin_mode(self._sdi, self.OUTPUT)
        ##     self.digital_write(self._sdi, self.LOW)
        ##     self.pin_mode(self._clk, self.OUTPUT)
        ##     self.digital_write(self._clk, self.HIGH)

