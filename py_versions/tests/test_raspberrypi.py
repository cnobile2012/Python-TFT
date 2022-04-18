#
# py_versions/tests/test_raspberrypi.py
#

import os
import sys
import unittest

from py_versions.raspberrypi import PiVersion


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
        path = "{}/export".format(self.GPIO_PIN_PATH)
        os.system("echo {} > {}".format(pin, path))

    def unset_pin(self, pin):
        path = "{}/unexport".format(self.GPIO_PIN_PATH)
        os.system("echo {} > {}".format(pin, path))

    def read_pin_value(self, pin):
        path = "{}/gpio{}/value".format(self.GPIO_PIN_PATH, pin)
        return os.popen("cat {}".format(path)).read()

    def read_direction(self, pin):
        path = "{}/gpio{}/direction".format(self.GPIO_PIN_PATH, pin)
        return os.popen("cat {}".format(path)).read()

    def test_pin_mode(self):
        """
        Test that pins can be set properly.
        """
        # Test OUTPUT direction with default set to HIGH.
        self._pyv.pin_mode(self.TEST_PIN, self._pyv.OUTPUT,
                           default=self._pyv.HIGH)
        expect_dir = self.DIR.get(self._pyv.OUTPUT)
        found_dir = self.read_direction(self.TEST_PIN)
        msg = "Direction should be '{}', found '{}'.".format(
            expect_dir, found_dir)
        self.assertEqual(expect_dir, found_dir, msg=msg)
        # Read value
        expect_val = self._pyv.HIGH
        found_val = self.read_pin_value(self.TEST_PIN)
        msg = "Value should be '{}', found '{}'.".format(expect_val, found_val)
        self.assertEqual(expect_val, found_val, msg=msg)
        # Test INPUT direction
        self._pyv.pin_mode(self.TEST_PIN, self._pyv.INPUT)
        expect_dir = self.DIR.get(self._pyv.INPUT)
        found_dir = self.read_direction(self.TEST_PIN)
        msg = "Direction should be '{}', found '{}'.".format(
            expect_dir, found_dir)
        self.assertEqual(expect_dir, found_dir, msg=msg)