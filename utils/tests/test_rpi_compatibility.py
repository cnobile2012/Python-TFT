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
        self._tft.set_board(Boards.ESP32)
        board = self._tft.get_board()
        msg = f"The board '{board}' does not match '{Boards.ESP32}'."
        self.assertEqual(board, Boards.ESP32, msg=msg)

    def test_unknown_set_board(self):
        """
        Test that an invalid board raises the proper exception.
        """
        with self.assertRaises(CompatibilityException) as cm:
            self._tft.set_board(1000) # Test with an out-of-range value.

    def test_spi_port_device(self):
        """
        Test that a proper pin mapping returns the correct port and device.

        # Second SPI buss
        dtoverlay=spi1-3cs

        The above line needs to be added to the `/boot/config.txt` on the RPI.
        """
        # Port 0
        port, device = self._tft.spi_port_device(self.CLK, None, None, self.CS)
        msg = f"The port should be '0', found '{port}'."
        self.assertEqual(0, port, msg=msg)
        msg = f"The device should be '0', found '{device}'."
        self.assertEqual(0, device, msg=msg)
        # Port 1
        port, device = self._tft.spi_port_device(21, None, None, 16)
        msg = f"The port should be '1', found '{port}'."
        self.assertEqual(1, port, msg=msg)
        msg = f"The device should be '2', found '{device}'."
        self.assertEqual(2, device, msg=msg)

    def test_invalid_spi_port_device(self):
        """
        Test that invalid arguments raises the proper exception.
        """
        with self.assertRaises(CompatibilityException) as cm:
            self._tft.spi_port_device(100, None, None, 101)

        msg = (f"Error message should be '{self._tft._SPI_PD_ERR_MSG}', "
               f"found '{str(cm.exception)}'.")
        self.assertEqual(self._tft._SPI_PD_ERR_MSG, str(cm.exception), msg=msg)
