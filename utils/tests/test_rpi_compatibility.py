#
# utils/tests/test_rpi_compatibility.py
#

import unittest

from ILI9225 import ILI9225
from utils import Boards, CompatibilityException


class TestBoards(unittest.TestCase):
    """
    Test class for the Boards class.
    """

    def __init__(self, name):
        super().__init__(name)

    def test_get_frequency(self):
        """
        Test that the correct frequence is returned for the board selected.
        """
        board = Boards.ARDUINO_ARCH_STM32F1
        freq = Boards._FREQUENCY.get(board)
        freq_found = Boards.get_frequency(board)
        msg = f"The board freq should be '{freq}', found '{freq_found}'."
        self.assertEqual(freq, freq_found, msg=msg)


class TestCompatibility(unittest.TestCase):
    """
    Test class for the Compatibility class using the Raspberry Pi.
    """
    RST = 17 # RTD
    RS = 27
    CS = 8
    MOSI = 10
    CLK = 11

    def __init__(self, name):
        super().__init__(name)

    def setUp(self):
        self._tft = ILI9225(self.RST, self.RS, self.CS, self.MOSI, self.CLK,
                            board=Boards.RASPI)
        self._tft.begin()

    def tearDown(self):
        self._tft.clear()
        self._tft.pin_cleanup()

    def test__get_board_name(self):
        """
        Test that the board name matches what was set.
        """
        board = self._tft._get_board_name()
        tmp_board = Boards._BOARDS.get(self._tft.BOARD)
        msg = f"The board '{board}' does not match '{tmp_board}'."
        self.assertEqual(board, tmp_board, msg=msg)

    def test_incorrect_get_board_name(self):
        """
        Test that the board name matches what was set.
        """
        board = self._tft._get_board_name(Boards.ARM)
        tmp_board = Boards._BOARDS.get(self._tft.BOARD)
        msg = f"The board '{board}' matches '{tmp_board}'."
        self.assertNotEqual(board, tmp_board, msg=msg)

    def test_get_board(self):
        """
        Test that the board value matches what was set.
        """
        board_val = self._tft.get_board()
        msg = f"The board '{board_val}' does not match '{self._tft.BOARD}'."
        self.assertEqual(board_val, self._tft.BOARD, msg=msg)

    def test_set_board(self):
        """
        Test that a board can be set.
        """
        try:
            self._tft.set_board(Boards.ESP32)
            board = self._tft.get_board()
            msg = f"The board '{board}' does not match '{Boards.ESP32}'."
            self.assertEqual(board, Boards.ESP32, msg=msg)
        finally:
            self._tft.set_board(Boards.RASPI)

    def test_unknown_set_board(self):
        """
        Test that an invalid board raises the proper exception.
        """
        with self.assertRaises(CompatibilityException) as cm:
            self._tft.set_board(1000) # Test with an out-of-range value.
