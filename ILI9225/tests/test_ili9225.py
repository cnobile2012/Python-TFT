#
# ILI9225/tests/test_ili9225.py
#

import unittest

from ILI9225 import ILI9225
from ILI9225.ili9225 import AutoIncMode, CurrentFont, GFXFont
from utils import (Boards, TFTException, CompatibilityException,
                   BGR16BitColor as Colors)


class TestAutoIncMode(unittest.TestCase):
    """
    Test the enumeration class.
    """

    def __init__(self, name):
        super().__init__(name)

    def test_number_of_enumerations(self):
        """
        Test that the class correctly enumerates the 8 values.
        """
        variables = [v for v in dir(AutoIncMode) if not v.startswith('_')]
        should = 8
        found = len(variables)
        msg = f"AutoIncMode should have {should} variables, found {found}"
        self.assertEqual(should, found, msg=msg)

    def test_enumerated_0_to_7(self):
        """
        Test that the enumeration range is from 0 to 7.
        """
        variables = [v for v in dir(AutoIncMode) if not v.startswith('_')]
        should = (0, 1, 2, 3, 4, 5, 6, 7)
        found = []

        for var in variables:
            obj = getattr(AutoIncMode, var)
            found.append(obj)

        found.sort()
        diff = [x for x in range(found[0], should[-1] + 1) if x not in found]
        diff += [x for x in found if x < should[0] or x > should[-1]]
        msg = f"Numbers missing or should not exist: {diff} not in {should}"
        self.assertFalse(diff, msg=msg)


class TestCurrentFont(unittest.TestCase):
    """
    Test the CurrentFont class.
    """

    def __init__(self, name):
        super().__init__(name)

    def test_empty_class(self):
        """
        Test that the empty class is set to the correct defaults.
        """
        cf = CurrentFont()
        variables = [v for v in dir(cf)
                     if not v.startswith('_') and not callable(getattr(cf, v))]

        for idx, v in enumerate(variables):
            if idx == 0:
                expect = ()
            elif idx == len(variables) -1:
                expect = False
            else:
                expect = 0

            found = getattr(cf, v)
            msg = (f"The {v} variable default value should be "
                   f"'{expect}', found '{found}'")
            self.assertEqual(expect, found, msg=msg)

    def test_instantiate_with_values(self):
        """
        Test that when instantiated the class has the correct values.
        """
        args = [[0, 1, 2, 3, 4], 1, 10, 3, 4, 4, True]
        cf = CurrentFont(font=args)
        variables = {'font': 0, 'width': 1, 'height': 2, 'offset': 3,
                     'numchars': 4, 'nbrows': 5, 'mono_sp': 6}
        expect = [[0, 1, 2, 3, 4], 1, 10, 3, 4, 5, True]

        for var, idx in variables.items():
            found = getattr(cf, var)
            msg = (f"The {var} variable value should be '{expect[idx]}', "
                   f"found '{found}'")
            self.assertEqual(expect[idx], found, msg=msg)


class TestILI9225(unittest.TestCase):
    """
    Test the main ILI9225 class.
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

    def _read_spi_buff(self, func_name=""):
        """
        This method is only used for testing when the board is a Raspberry Pi
        otherwise it will raise an exception, so don't use it.
        """
        self._tft._spi_buff.flush()
        ret = self._tft._spi_buff.getvalue()
        self._tft._spi_buff.truncate(0)
        self._tft._spi_buff.seek(0)
        return f'{func_name}\n{ret}'

    def test_clear(self):
        """
        Test that the screen clears to black.
        """
        x = self._tft.LCD_WIDTH / 2
        y = self._tft.LCD_HEIGHT / 2
        self._tft.draw_circle(x, y, 80, Colors.RED)
        ret = self._read_spi_buff('test_clear')
        self._tft.clear()
        ret = self._read_spi_buff('test_clear')
        print(ret)
