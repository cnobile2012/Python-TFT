#
# utils/tests/test_rpi_compatibility.py
#

import unittest

from ILI9225 import ILI9225
from utils.compatibility import Compatibility
from utils import Boards, CompatibilityException


class TestBoards(unittest.TestCase):
    """
    Test class for the Boards class.
    """

    def __init__(self, name):
        super().__init__(name)

    #@unittest.skip("Temporary")
    def test_get_board_name(self):
        """
        Test that the correct board name is returned with a board id.
        """
        board_id = 9
        expect = Boards._BOARDS.get(board_id)[0]
        found = Boards.get_board_name(board_id)
        msg = f"Expect '{expect}' found '{found}'"
        self.assertEqual(expect, found, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_board_id(self):
        """
        Test that the correct board id is returned with the board name.
        """
        board_name = 'RASPI'
        expect = Boards._BOARD_IDS.get(board_name)
        found = Boards.get_board_id(board_name)
        msg = f"Expect '{expect}' found '{found}'"
        self.assertEqual(expect, found, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_frequencies(self):
        """
        Test that the correct frequence is returned for the board selected.
        """
        port = 1
        board = Boards.ARDUINO_STM32_FEATHER
        freq = Boards._BOARDS.get(board)[1][port]
        freq_found = Boards.get_frequency(board, port)
        msg = f"The board freq should be '{freq}', found '{freq_found}'."
        self.assertEqual(freq, freq_found, msg=msg)


class TestCompatibility(unittest.TestCase):
    """
    Test class for the Compatibility class using the Raspberry Pi.
    """
    RST = 17 # RTD
    RS = 27
    PORT = 0
    CS = 8

    def __init__(self, name):
        super().__init__(name)

    def setUp(self):
        Compatibility.ERROR_MSGS = ILI9225.ERROR_MSGS
        self._com = Compatibility()
        self._spi_port = self.PORT

    def tearDown(self):
        self._com.pin_cleanup()

    #@unittest.skip("Temporary")
    def test__get_board_name(self):
        """
        Test that the board name matches what was set.
        """
        expect_board = Boards._BOARDS.get(self._com.BOARD)[0]
        found_board = self._com._get_board_name()
        msg = f"Expect '{expect_board}' found '{found_board}'."
        self.assertEqual(expect_board, found_board, msg=msg)

    #@unittest.skip("Temporary")
    def test_incorrect_get_board_name(self):
        """
        Test that the board name matches what was set.
        """
        expect_board = Boards._BOARDS.get(self._com.BOARD)[0]
        found_board = self._com._get_board_name(Boards.ARDUINO_STM32_FEATHER)
        msg = f"Expect '{expect_board}' found '{found_board}'."
        self.assertNotEqual(expect_board, found_board, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_board(self):
        """
        Test that the board value matches what was set.
        """
        expect_board = self._com.BOARD
        found_board = self._com.get_board()
        msg = f"Expect '{expect_board}' found '{found_board}'."
        self.assertEqual(expect_board, found_board, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_board(self):
        """
        Test that a board ID can be set.
        """
        try:
            self._com.set_board(Boards.ESP32)
            found_board = self._com.get_board()
            msg = f"Expect '{Boards.ESP32}' found '{found_board}'."
            self.assertEqual(Boards.ESP32, found_board, msg=msg)
        finally:
            self._com.set_board(Boards.RASPI)

    #@unittest.skip("Temporary")
    def test_unknown_set_board(self):
        """
        Test that an invalid board raises the proper exception.
        """
        with self.assertRaises(CompatibilityException) as cm:
            self._com.set_board(1000) # Test with an out-of-range value.

        board_name = self._com._get_board_name(self._com.BOARD)
        expect_msg = self._com.ERROR_MSGS['BRD_UNSUP'].format(board_name)
        found_msg = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found_msg}'"
        self.assertEqual(expect_msg, found_msg, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_get_pwm_frequency(self):
        """
        Test that the getter and setter are both working properly.
        """
        # Store the default frequency
        default_freq = self._com.pwm_frequency
        # Test a different frequency
        expect_freq = 100000
        self._com.pwm_frequency = expect_freq
        found_freq = self._com.pwm_frequency
        msg = f"Expect '{expect_freq}' found '{found_freq}'"
        self.assertEqual(expect_freq, found_freq, msg=msg)
        # Revert to original frequency
        self._com.pwm_frequency = default_freq
        found_freq = self._com.pwm_frequency
        msg = f"Expect '{default_freq}' found '{found_freq}'"
        self.assertEqual(default_freq, found_freq, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_get_spi_frequency(self):
        """
        Test that the getter and setter are both working properly.
        """
        # Store the default frequency
        default_freq = self._com.spi_frequency
        # Test a different frequency
        expect_freq = 40000000
        self._com.spi_frequency = expect_freq
        found_freq = self._com.spi_frequency
        msg = f"Expect '{expect_freq}' found '{found_freq}'"
        self.assertEqual(expect_freq, found_freq, msg=msg)
        # Revert to original frequency
        self._com.spi_frequency = default_freq
        found_freq = self._com.spi_frequency
        msg = f"Expect '{default_freq}' found '{found_freq}'"
        self.assertEqual(default_freq, found_freq, msg=msg)

    #@unittest.skip("Temporary")
    def test_error_set_spi_frequency(self):
        """
        Test that when an out-of-range port is provided that an
        exception is raised.
        """
        with self.assertRaises(CompatibilityException) as cm:
            self._com._spi_port = 5 # TRhis is an invalid port for the RPI
            self._com.spi_frequency()

        board_name = self._com._get_board_name(self._com.BOARD)
        expect_msg = self._com.ERROR_MSGS['INV_PORT'].format(board_name)
        found_msg = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found_msg}'"
        self.assertEqual(expect_msg, found_msg, msg=msg)

    #@unittest.skip("Temporary")
    def test_ESP32_get_spi_frequency(self):
        """
        Test that an ESP32 can get the correct frequency without
        raising an exception.
        """
        # Test for an ESP32 (We need to fudge a few values on the
        # Compatibility class object).
        self._com.BOARD = Boards.ESP32
        self._com._spi_port = 2
        expect_freq = Boards._BOARD_SPECS[7][1]
        found_freq = self._com.spi_frequency
        msg f"Expect '{expect_freq}' found '{found_freq}'"
        self.assertEqual(expect_freq, found_freq, msg=msg)
