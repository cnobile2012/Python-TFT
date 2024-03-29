#
# py_versions/tests/test_raspberrypi.py
#

import os
import io
import math
import time
import unittest

from contextlib import redirect_stdout

from utils.common import CommonMethods, Boards, CompatibilityException
from py_versions.raspberrypi import PiVersion

from RPi import GPIO


def timeit(method):
    """
    This method declares a method or function decorator.
    """
    def timed(*args, **kw):
        import sys
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        diff = (te - ts) * 1000 # MS results

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int(diff)
        else:
            #sys.stdout.write(f"{method.__name__}  {diff:2.2f} ms\n")
            sys.stdout.write(f"{diff:2.2f}")

        return result
    return timed


class TestPiVersion(unittest.TestCase):
    """
    Test class for the Raspberry Pi PiVersion class.
    """
    RST = 17 # RTD
    RS = 27
    PORT = 0
    CS = 8
    LED = 22
    TEST_PIN = 24 # Not used in TFT code.
    GPIO_PIN_PATH = "/sys/class/gpio"
    DIR = {0: 'out', 1: 'in'}

    def __init__(self, name):
        super().__init__(name)

    @classmethod
    def setUpClass(cls):
        GPIO.setwarnings(False)

    @classmethod
    def tearDownClass(cls):
        GPIO.setwarnings(True)

    def setUp(self):
        PiVersion.TESTING = True
        PiVersion.ERROR_MSGS = CommonMethods.ERROR_MSGS
        PiVersion.BOARD = Boards.RASPI
        PiVersion.MAX_BRIGHTNESS = 255
        self._pyv = PiVersion()
        self.setup_pin(self.TEST_PIN)
        # The following values need to be set since they won't be on
        # the object because the parent object is not there.
        self._pyv._rst = self.RST
        self._pyv._rs = self.RS
        self._pyv._spi_port = self.PORT
        self._pyv._cs = self.CS
        self._pyv._led = self.LED
        self._pyv.pwm_frequency = self._pyv._DEF_PWM_FREQ
        self._pyv.spi_frequency = Boards.get_frequency(
            self._pyv.BOARD, self._pyv._spi_port)
        self._pyv.pin_mode(self._pyv._cs, self._pyv.OUTPUT)
        GPIO.setup(self._pyv._rs, GPIO.OUT, pull_up_down=GPIO.PUD_OFF)

    def tearDown(self):
        self.unset_pin(self.TEST_PIN)
        self._pyv = None
        GPIO.cleanup(self.TEST_PIN)

    def setup_pin(self, pin):
        path = f"{self.GPIO_PIN_PATH}/export"
        os.system(f"echo {pin} > {path}")

    def unset_pin(self, pin):
        path = f"{self.GPIO_PIN_PATH}/unexport"
        os.system(f"echo {pin} > {path}")

    def read_pin_value(self, pin):
        path = f"{self.GPIO_PIN_PATH}/gpio{pin}/value"
        return int(os.popen(f"cat {path}").read().strip())

    def read_direction(self, pin):
        path = f"{self.GPIO_PIN_PATH}/gpio{pin}/direction"
        return os.popen(f"cat {path}").read().strip()

    #@unittest.skip("Temporary")
    def test_pin_mode(self):
        """
        Test that pins can be set properly.
        """
        # Test OUTPUT direction with default set to HIGH.
        self._pyv.pin_mode(self.TEST_PIN, self._pyv.OUTPUT,
                           default=self._pyv.HIGH)
        expect_dir = self.DIR.get(self._pyv.OUTPUT)
        found_dir = self.read_direction(self.TEST_PIN)
        msg = f"Direction should be '{expect_dir}', found '{found_dir}'."
        self.assertEqual(expect_dir, found_dir, msg=msg)
        # Read value
        expect_val = self._pyv.HIGH
        found_val = self.read_pin_value(self.TEST_PIN)
        msg = f"Value should be '{expect_val}', found '{found_val}'."
        self.assertEqual(expect_val, found_val, msg=msg)
        # Test INPUT direction
        self._pyv.pin_mode(self.TEST_PIN, self._pyv.INPUT)
        expect_dir = self.DIR.get(self._pyv.INPUT)
        found_dir = self.read_direction(self.TEST_PIN)
        msg = f"Direction should be '{expect_dir}', found '{found_dir}'."
        self.assertEqual(expect_dir, found_dir, msg=msg)

    #@unittest.skip("Temporary")
    def test_digital_write(self):
        """
        Test that a digital write to a pin works properly.
        """
        # Set pin mode.
        self._pyv.pin_mode(self.TEST_PIN, self._pyv.OUTPUT)
        # Run method under test set to HIGH.
        self._pyv.digital_write(self.TEST_PIN, self._pyv.HIGH)
        expect = self._pyv.HIGH
        found = self.read_pin_value(self.TEST_PIN)
        msg = f"Pin {self.TEST_PIN} expected '{expect}' found '{found}'"
        self.assertEqual(expect, found, msg=msg)
        # Run method under test set to LOW.
        self._pyv.digital_write(self.TEST_PIN, self._pyv.LOW)
        expect = self._pyv.LOW
        found = self.read_pin_value(self.TEST_PIN)
        msg = f"For pin {self.TEST_PIN} expected '{expect}' found '{found}'"
        self.assertEqual(expect, found, msg=msg)

    #@unittest.skip("Temporary")
    def test_delay(self):
        """
        Test that the delay in MS is correct.
        """
        buff = io.StringIO()
        ms = 10

        with redirect_stdout(buff):
            @timeit
            def run_it():
                self._pyv.delay(ms)

            run_it()

        found = buff.getvalue()
        found = float(found) if len(found) else 0.0
        buff.close()
        approx = 0.40
        msg = f"Expected '{ms} within {approx} ms' found: {found}"
        self.assertTrue(math.isclose(ms, found, abs_tol=approx), msg)

    #@unittest.skip("Temporary")
    def test__spi_port_device(self):
        """
        Test that a proper pin mapping returns the correct device.

        # Second SPI buss
        dtoverlay=spi1-3cs

        The above line needs to be added to the `/boot/config.txt` on the RPI.
        """
        # Port 0
        expected_device = 0
        self._pyv._spi_port_device()
        msg = (f"The device should be '{expected_device}', "
               f"found '{self._pyv._device}'.")
        self.assertEqual(0, self._pyv._device, msg=msg)
        # Port 1
        expected_port = 1
        self._pyv._spi_port = expected_port
        expected_device = 2
        self._pyv._cs = 16
        self._pyv._spi_port_device()
        msg = (f"The device should be '{expected_device}', "
               f"found '{self._pyv._device}'.")
        self.assertEqual(expected_device, self._pyv._device, msg=msg)

    #@unittest.skip("Temporary")
    def test_invalid_port__spi_port_device(self):
        """
        Test that an invalid port raises the proper exception.
        """
        self._pyv._spi_port = 100

        with self.assertRaises(CompatibilityException) as cm:
            self._pyv._spi_port_device()

        expected_msg = self._pyv.ERROR_MSGS['INV_PORT'].format(
                Boards.get_board_name(self._pyv.BOARD))
        msg = f"'{expected_msg}' != '{str(cm.exception)}'"
        self.assertEqual(expected_msg, str(cm.exception), msg=msg)

    #@unittest.skip("Temporary")
    def test_invalid_cs__spi_port_device(self):
        """
        Test that an invalid CS pin raises the proper exception.
        """
        self._pyv._cs = 101

        with self.assertRaises(CompatibilityException) as cm:
            self._pyv._spi_port_device()

        expected_msg = ("Invalid cs pin '{}' selection for port '{}'."
                        ).format(self._pyv._cs, self._pyv._spi_port)
        msg = f"'{expected_msg}' != '{str(cm.exception)}'"
        self.assertEqual(expected_msg, str(cm.exception), msg=msg)

    #@unittest.skip("Temporary")
    def test_spi_start_end_is_connected(self):
        """
        Test that an SPI connection can be opened and closed and checked.
        """
        self._pyv._spi_port_device()

        try:
            self._pyv.spi_start_transaction()
            expect = 0xFFFF
            found = self._pyv.spi_write(bytearray(expect.to_bytes(2, 'big')))
            exists = self._pyv.is_spi_connected
            msg = f"Expect {expect} found {found} exists {exists}"
            self.assertEqual(expect, found[0], msg=msg)
            self.assertTrue(exists, msg=msg)
        finally:
            self._pyv.spi_end_transaction()
            exists = self._pyv.is_spi_connected
            msg = f"Exists {exists}"
            self.assertFalse(exists, msg=msg)

    #@unittest.skip("Temporary")
    def test_spi_write(self):
        """
        Test that writing data to the SPI port works properly.
        """
        self._pyv._spi_port_device()

        try:
            # Test non sequence value
            self._pyv.spi_start_transaction()
            expect = 0xFFFF
            found = self._pyv.spi_write(bytearray(expect.to_bytes(2, 'big')))
            msg = f"Expect {expect} found {found}"
            self.assertEqual(expect, found[0], msg=msg)
            # Test a bytearray
            expect = [0xAAAA, 0xBBBB, 0xCCCC]
            array = bytearray()

            for value in expect:
                array.append(value >> 8)
                array.append(value & 0xFF)

            found = self._pyv.spi_write(array)
            msg = f"Expect {expect} found {found}"
            self.assertEqual(expect, found, msg=msg)
        finally:
            self._pyv.spi_end_transaction()

    #@unittest.skip("Temporary")
    def test_setup_pwm(self):
        """
        Test that a PWM pin gets setup properly.
        """
        freq = self._pyv.pwm_frequency
        num_reps = 1000
        brightness = 128.0
        expect_percent = 50.0
        sleep = freq / num_reps * 0.0000034

        try:
            # Set brightness to 128 -- 50%
            self.setup_pin(self.LED)
            self._pyv.pin_mode(self.LED, self._pyv.OUTPUT)
            self._pyv.setup_pwm(self.LED, brightness)
            readings = [self.read_pin_value(self.LED) for c in range(num_reps)
                        if not time.sleep(sleep)]
            percent = min(readings.count(0), readings.count(1)
                          ) * 100 / num_reps
            print(expect_percent, percent)
            msg = f"Expect abount {expect_percent}% found {percent}%"
            self.assertTrue(
                math.isclose(expect_percent, percent, rel_tol=5), msg=msg)
        finally:
            self.unset_pin(self.LED)

    #@unittest.skip("Temporary")
    def test_change_led_duty_cycle(self):
        """
        Test that a PWM pin gets setup properly.
        """
        freq = self._pyv.pwm_frequency
        num_reps = 1000
        brightness = 128.0
        expect_percent = 50.0
        sleep = freq / num_reps * 0.0000034

        try:
            # Set brightness to 128 -- 50%
            self.setup_pin(self.LED)
            self._pyv.pin_mode(self.LED, self._pyv.OUTPUT)
            self._pyv.setup_pwm(self.LED, brightness)
            readings = [self.read_pin_value(self.LED) for c in range(num_reps)
                        if not time.sleep(sleep)]
            percent = min(readings.count(0), readings.count(1)
                          ) * 100 / num_reps
            print(expect_percent, percent)
            msg = f"Expect abount {expect_percent}% found {percent}%"
            self.assertTrue(
                math.isclose(expect_percent, percent, rel_tol=5), msg=msg)
            # Set brightness to 64 -- 25%
            brightness /= 2
            expect_percent /= 2
            self._pyv.change_led_duty_cycle(brightness)
            readings = [self.read_pin_value(self.LED) for c in range(num_reps)
                        if not time.sleep(sleep)]
            percent = min(readings.count(0), readings.count(1)
                          ) * 100 / num_reps
            print(expect_percent, percent)
            msg = f"Expect abount {expect_percent}% found {percent}%"
            self.assertTrue(expect_percent < percent, msg=msg)
        finally:
            self.unset_pin(self.LED)
