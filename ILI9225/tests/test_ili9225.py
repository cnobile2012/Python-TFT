#
# ILI9225/tests/test_ili9225.py
#

import unittest
import re

from collections import OrderedDict

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

    All tests must have the MOSI redirected to MISO on the Raspberry Pi.
    """
    RST = 17 # RTD
    RS = 27
    CS = 8
    MOSI = 10
    CLK = 11

    REGEX_DATA = re.compile(
        r"Command: (0x[\dA-Fa-f]+)|   Data: (0x[\dA-Fa-f]+)")

    CMD_NAMES = [cmd for cmd in dir(ILI9225) if cmd.startswith('CMD_')]
    CMD_NAMES_REV = {getattr(ILI9225, n): n for n in CMD_NAMES}

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

    def _find_data(self, values):
        """
        With this data:
        s = '''
        ...: test_clear
        ...: Command: 0x3
        ...:    Data: 0x1038
        ...: Command: 0x36
        ...:    Data: 0xaf
        ...: Command: 0x37
        ...:    Data: 0x0
        ...: Command: 0x38
        ...:    Data: 0xdb
        ...: Command: 0x39
        ...:    Data: 0x0
        ...: Command: 0x20
        ...:    Data: 0x0
        ...: Command: 0x21
        ...:    Data: 0x0
        ...: Command: 0x22
        ...:    Data: 0x0
        ...:    Data: 0x0'''

        The response is (Variable Name, [Variable code, Variable Values, ...]):
        OrderedDict([('CMD_ENTRY_MODE', [3, 4152]),
                     ('CMD_HORIZONTAL_WINDOW_ADDR1', [54, 175]),
                     ('CMD_HORIZONTAL_WINDOW_ADDR2', [55, 0]),
                     ('CMD_VERTICAL_WINDOW_ADDR1', [56, 219]),
                     ('CMD_VERTICAL_WINDOW_ADDR2', [57, 0]),
                     ('CMD_RAM_ADDR_SET1', [32, 0]),
                     ('CMD_RAM_ADDR_SET2', [33, 0]),
                     ('CMD_GRAM_DATA_REG', [34, 0, 0])])
        """
        data = self.REGEX_DATA.findall(values)
        cmd_hash = OrderedDict()

        if data:
            item = {}

            for line in data:
                if line[0] != '':
                    item.clear()
                    cmd = eval(line[0])
                    dt = [cmd]
                    item[self.CMD_NAMES_REV.get(cmd)] = dt
                else:
                    dt.append(eval(line[1]))

                cmd_hash.update(item)

        return cmd_hash

    def test_clear(self):
        """
        Test that the screen clears to black.
        """
        self._tft.clear()
        ret = self._read_spi_buff('test_clear')
        data = self._find_data(ret)
        expect = (
            (self._tft.CMD_ENTRY_MODE, 1, 0x1038),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR1, 1, 0xaf),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR2, 1, 0x00),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR1, 1, 0xdb),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR2, 1, 0x00),
            (self._tft.CMD_RAM_ADDR_SET1, 1, 0x00),
            (self._tft.CMD_RAM_ADDR_SET2, 1, 0x00),
            (self._tft.CMD_GRAM_DATA_REG, 38720 , 0x00),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR1, 1, 0xaf),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR2, 1, 0x00),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR1, 1, 0xdb),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR2, 1, 0x00)
            )
        msg1 = "Command {}--should be: {}, found: {}"
        msg2 = "Command {}: data should be: {}, found: {}"

        # item = [Variable code, Variable Values, ...]
        for idx, (name, item) in enumerate(data.items()):
            # Test for variable name and code
            expect_code = expect[idx][0]
            expect_name = self.CMD_NAMES_REV.get(expect_code)
            found_code = item[0]
            msg1_tmp = msg1.format(expect_name, expect_code, found_code)
            self.assertEqual(expect_code, found_code, msg=msg1_tmp)

            # Test for values
            for value in range(expect[idx][1]):
                msg2_tmp = msg2.format(expect_name, expect[idx][2], item[1])
                self.assertEqual(expect[idx][2], item[1], msg=msg2_tmp)



