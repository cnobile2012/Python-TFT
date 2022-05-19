#
# py_versions/tests/test_raspberrypi.py
#

import os
import io
import unittest
from contextlib import redirect_stdout

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
        self._pyv = PiVersion()
        self.setup_pin(self.TEST_PIN)

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
        msg = f"Expected '{ms}' found: {found}"
        self.assertTrue(ms == found, msg)
