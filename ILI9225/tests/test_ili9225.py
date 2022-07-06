#
# ILI9225/tests/test_ili9225.py
#

import os
import re
import unittest

from ILI9225 import (ILI9225, Boards, TFTException, CompatibilityException,
                     Terminal12x16, BGR16BitColor, RGB16BitColor as Colors)
from ILI9225.ili9225 import AutoIncMode, CurrentFont, GFXFont, GFXGlyph
from fonts.FreeSerifItalic18pt7b import FreeSerifItalic18pt7b
from fonts.FreeSansBold10pt7b import FreeSansBold10pt7b


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
    PORT = 0
    CS = 8
    LED = 22

    REGEX_DATA = re.compile(
        r"Command: (0?x?[\dA-Fa-f]+)|   Data: (0?x?[\dA-Fa-f]+)")
    REGEX_REPR = re.compile(r"^.+the (?P<platform>.+) platform.+$")
    REGEX_PARSE = re.compile(r"(self._tft\.\w+), ([ ,\w]+)")

    CMD_NAMES = [cmd for cmd in dir(ILI9225) if cmd.startswith('CMD_')]
    CMD_NAMES_REV = {getattr(ILI9225, n): n for n in CMD_NAMES}

    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, name):
        super().__init__(name)

    def setUp(self):
        self._tft = ILI9225(self.RST, self.RS, self.PORT, self.CS,
                            led=self.LED, board=Boards.RASPI)
        self._tft.begin()
        self._read_spi_buff('dummy') # Clear the previous data.

    def tearDown(self):
        self._tft.clear()
        self._tft.pin_cleanup()

    def _read_data_file(self, filename):
        with open(f"{self.CURRENT_PATH}/{filename}", 'r') as f:
            result = f.read()

        cmd_list = []
        items = self.REGEX_PARSE.findall(
            result.replace("\n", "").replace("   ", ""))

        if items:
            for cmd, data in items:
                cmd = cmd.replace('self._tft.', '')
                num_cmd = eval(f"ILI9225.{cmd}")
                cmds = [num_cmd]
                cmd_list.append(cmds)

                for item in eval(data):
                    cmds.append(item)
        else:
            # Throw away the name.
            for name, cmd, value_list in eval(result):
                cmds = [cmd]
                cmd_list.append(cmds)
                num_count = 0
                saved_val = None
                data_len = len(value_list)

                for idx, value in enumerate(value_list, start=1):
                    num_count += 1

                    if saved_val is None:
                        saved_val = value
                    elif saved_val != value or idx == data_len:
                        if idx != data_len:
                            num_count -= 1

                    cmds.append(num_count)
                    cmds.append(saved_val)
                    num_count = 1
                    saved_val = value

        return cmd_list

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
        value = '''
            test_clear
            Command: 0x3
               Data: 0x1038
            Command: 0x36
               Data: 0xaf
            Command: 0x37
               Data: 0x0
            Command: 0x38
               Data: 0xdb
            Command: 0x39
               Data: 0x0
            Command: 0x20
               Data: 0x0
            Command: 0x21
               Data: 0x0
            Command: 0x22
               Data: 0x0
               Data: 0x0'''

        The response is [Variable Name, Variable code, [Variable Values, ...]]:
        [
         ['CMD_ENTRY_MODE', [3, 4152]],
         ['CMD_HORIZONTAL_WINDOW_ADDR1', [54, 175]],
         ['CMD_HORIZONTAL_WINDOW_ADDR2', [55, 0]],
         ['CMD_VERTICAL_WINDOW_ADDR1', [56, 219]],
         ['CMD_VERTICAL_WINDOW_ADDR2', [57, 0]],
         ['CMD_RAM_ADDR_SET1', [32, 0]],
         ['CMD_RAM_ADDR_SET2', [33, 0]],
         ['CMD_GRAM_DATA_REG', [34, 0, 0]]
        ]
        """
        data = self.REGEX_DATA.findall(values)
        cmds = []

        if data:
            for line in data:
                if line[0] != '':
                    cmd = eval(line[0])
                    item = []
                    dt = []
                    item.append(self.CMD_NAMES_REV.get(cmd))
                    item.append(cmd)
                    item.append(dt)
                    cmds.append(item)
                else:
                    dt.append(eval(line[1]))

        return cmds

    def _run_spi_test(self, expect, func_name, idx=None):
        ret = self._read_spi_buff(func_name)
        data = self._find_data(ret)
        expect_len = len(expect)
        data_len = len(data)
        msg = (f"Expected length {expect_len} is not equal to found "
               f"length {data_len}, data '{data}'")
        msg += f" index {idx}" if idx is not None else ""
        self.assertEqual(expect_len, data_len, msg=msg)
        msg1 = "Command {}--should be: {}, found: {}, item: {}"
        msg2 = "Command {}--data should be: {}, found: {}"
        msg3 = "Command {}--number of states not even, found {}"

        # item = [Variable Name, Variable code, [Variable Values, ...]]
        for idx, item in enumerate(data):
            # Test for variable name and code
            expect_code = expect[idx][0]
            expect_name = self.CMD_NAMES_REV.get(expect_code)
            found_code = item[1] # Command code
            msg1_tmp = msg1.format(expect_name, expect_code, found_code, item)
            self.assertEqual(expect_code, found_code, msg=msg1_tmp)

            # Test for number of states of values
            states = len(expect[idx][1:]) % 2
            msg3_tmp = msg3.format(expect_name, states)
            self.assertFalse(states, msg=msg3_tmp)

            # Test for values
            for num in range(1, states, 2):
                expect_value = expect[idx][num + 1]

                for j in range(expect[idx][num]):
                    found_value = item[2][j]
                    msg2_tmp = msg2.format(
                        expect_name, expect_value, found_value)
                    self.assertEqual(expect_value, found_value, msg=msg2_tmp)

    #@unittest.skip("Temporary")
    def test___init__(self):
        """
        Test that an invalid board is passed into the constructor.
        """
        invalid_board = 1000

        with self.assertRaises(CompatibilityException) as cm:
            tft = ILI9225(self.RST, self.RS, self.PORT, self.CS, invalid_board)

        board_name = self._tft._get_board_name(invalid_board)
        expect_msg = self._tft.ERROR_MSGS['BRD_UNSUP'].format(board_name)
        found = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found}'"
        self.assertEqual(expect_msg, found, msg=msg)

    #@unittest.skip("Temporary")
    def test_clear(self):
        """
        Test that the screen clears to black.
        """
        self._tft.clear()
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
        self._run_spi_test(expect, 'test_set_display')

    #@unittest.skip("Temporary")
    def test_set_display_background(self):
        """
        Test that the background can be changed to a different color
        other than black.
        """
        self._tft.set_display_background(Colors.VIOLET) # 0xEC1D
        expect = (
            (self._tft.CMD_ENTRY_MODE, 1, 0x1038),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR1, 1, 0xaf),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR2, 1, 0x00),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR1, 1, 0xdb),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR2, 1, 0x00),
            (self._tft.CMD_RAM_ADDR_SET1, 1, 0x00),
            (self._tft.CMD_RAM_ADDR_SET2, 1, 0x00),
            (self._tft.CMD_GRAM_DATA_REG, 38720 , 0xec1d),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR1, 1, 0xaf),
            (self._tft.CMD_HORIZONTAL_WINDOW_ADDR2, 1, 0x00),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR1, 1, 0xdb),
            (self._tft.CMD_VERTICAL_WINDOW_ADDR2, 1, 0x00)
            )
        self._run_spi_test(expect, 'test_set_display_background')

    #@unittest.skip("Temporary")
    def test_set_backlight(self):
        """
        Test that the backlight variable is set to eithe True or False.
        """
        # Test initial value.
        value = self._tft._bl_state
        msg = f"Should be 'True' found '{value}'"
        self.assertTrue(value, msg=msg)
        # Test set to False.
        self._tft.set_backlight(False)
        value = self._tft._bl_state
        msg = f"Should be 'False' found '{value}'"
        self.assertFalse(value, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_backlight_with_brightness(self):
        """
        Test that the backlight brightness variable has been set properly.
        """
        # Test initial value.
        value = self._tft.brightness
        msg = f"Should be 'self._tft.MAX_BRIGHTNESS' found '{value}'"
        self.assertEqual(self._tft.MAX_BRIGHTNESS, value, msg=msg)
        # Test set to 50%
        expected_value = (self._tft.MAX_BRIGHTNESS + 1) / 2
        self._tft.set_backlight(True, expected_value)
        value = self._tft.brightness
        msg = f"Should be '{expected_value}' found '{value}'"
        self.assertEqual(expected_value, value, msg=msg)
        # Test set to 100%
        expected_value = self._tft.MAX_BRIGHTNESS
        self._tft.set_backlight(True, expected_value)
        value = self._tft.brightness
        msg = f"Should be '{expected_value}' found '{value}'"
        self.assertEqual(expected_value, value, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_brightness(self):
        """
        Test that the brightness is returned through the property.
        """
        brightness = self._tft.brightness # Just grab the default
        msg = f"Expect 0..255 found {brightness}"
        self.assertTrue(0 <= brightness <= self._tft.MAX_BRIGHTNESS, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_brightness(self):
        """
        Test that brightness property is set with a value between 0..255.
        """
        for brightness in range(512, 10):
            self._tft.brightness = brightness
            found = self._tft.brightness
            msg = f"Expect 0..255 found {found}"
            self.assertTrue(0 <= brightness <= self._tft.MAX_BRIGHTNESS,
                            msg=msg)

    #@unittest.skip("Temporary")
    def test_set_display(self):
        """
        Test that the display can be turned on and off.
        """
        # Test that the display is off then on.
        self._tft.set_display(False)
        self._tft.set_display(True)
        expect = (
            (0x00ff, 1, 0x0000), # Off
            (self._tft.CMD_DISP_CTRL1, 1, 0x0000),
            (self._tft.CMD_POWER_CTRL1, 1, 0x0003),
            (0x00ff, 1, 0x0000), # On
            (self._tft.CMD_POWER_CTRL1, 1, 0x0000),
            (self._tft.CMD_DISP_CTRL1, 1, 0x1017)
            )
        self._run_spi_test(expect, 'test_set_display')

    #@unittest.skip("Temporary")
    def test_orientation(self):
        """
        Test that the orientation property can be set to all four
        orientations.

        We make five checks in this order 3, 1, 2, 0, and then 500 which
        should be equal to 0 because of the modulo in the code.
        """
        tests = (
            ((3, 1), self._tft.LCD_HEIGHT, self._tft.LCD_WIDTH),
            ((2, 0, 500), self._tft.LCD_WIDTH, self._tft.LCD_HEIGHT)
            )

        for orient, x, y in tests:
            for orientation in orient:
                self._tft.orientation = orientation
                msg = (f"Should be orientation {orientation}: '{x}' "
                       f"found '{self._tft._max_x}'")
                self.assertEqual(x, self._tft._max_x, msg=msg)
                msg = (f"Should be orientation {orientation}: '{y}' "
                       f"found '{self._tft._max_y}'")
                self.assertEqual(y, self._tft._max_y, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_orientation(self):
        """
        Test that the current correct orientation is returned.
        """
        tests = ((3, 3), (2, 2), (1, 1), (0, 0), (500, 0))

        for orient, expect in tests:
            self._tft.orientation = orient
            orientation = self._tft.orientation
            msg = f"Expect '{expect}' found '{orientation}'"
            self.assertEqual(expect, orientation, msg=msg)

    #@unittest.skip("Temporary")
    def test__orient_coordinates(self):
        """
        Test that the orientation coordinates are set correctly.
        """
        x = 10
        y = 100
        tests = (
            (3, y, self._tft.LCD_HEIGHT - x - 1),
            (2, self._tft.LCD_WIDTH - x - 1, self._tft.LCD_HEIGHT - y - 1),
            (1, self._tft.LCD_WIDTH - y - 1, x),
            (0, x, y),
            (500, x, y)
            )

        for orient, xx, yy in tests:
            self._tft.orientation = orient
            xxx, yyy = self._tft._orient_coordinates(x, y)
            msg = f"Orientation '{orient}': Expect x = {xx} found x = {xxx}"
            self.assertEqual(xx, xxx, msg=msg)
            msg = f"Orientation '{orient}': Expect y = {yy} found y = {yyy}"
            self.assertEqual(yy, yyy, msg=msg)

    #@unittest.skip("Temporary")
    def test_display_max_x(self):
        """
        Test that the max x is correct depending on the set orientation.
        """
        tests = (
            (3, self._tft.LCD_HEIGHT),
            (2, self._tft.LCD_WIDTH),
            (1, self._tft.LCD_HEIGHT),
            (0, self._tft.LCD_WIDTH),
            (500, self._tft.LCD_WIDTH)
            )

        for orientation, xx in tests:
            self._tft.orientation = orientation
            xxx = self._tft.display_max_x
            msg = f"Expect x = {xx} found x = {xxx}"
            self.assertEqual(xx, xxx, msg=msg)

    #@unittest.skip("Temporary")
    def test_display_max_y(self):
        """
        Test that the max y is correct depending on the set orientation.
        """
        tests = (
            (3, self._tft.LCD_WIDTH),
            (2, self._tft.LCD_HEIGHT),
            (1, self._tft.LCD_WIDTH),
            (0, self._tft.LCD_HEIGHT),
            (500, self._tft.LCD_HEIGHT)
            )

        for orientation, yy in tests:
            self._tft.orientation = orientation
            yyy = self._tft.display_max_y
            msg = f"Expect y = {yy} found y = {yyy}"
            self.assertEqual(yy, yyy, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_get_font(self):
        """
        Test that the current standard font's set and get work properly.
        """
        tests = (
            ('Terminal12x16', Terminal12x16, False),
            ('Terminal12x16', Terminal12x16, True)
            )

        for name, full_font, mono in tests:
            self._tft.set_font(full_font, mono_sp=mono)
            font = full_font
            width = full_font[0]
            height = full_font[1]
            offset = full_font[2]
            numchars = full_font[3]
            rnd_height = height // 8
            nbrows = rnd_height + 1 if height % 8 else rnd_height
            mono_sp = mono
            cfont = self._tft.get_font()
            msg = (f"Font {name}: len(font) Expects '{len(font)}' "
                   f"found '{len(cfont.font)}'")
            self.assertEqual(len(font), len(cfont.font), msg=msg)
            msg = (f"Font {name}: width Expects '{width}' "
                   f"found '{cfont.width}'")
            self.assertEqual(width, cfont.width, msg=msg)
            msg = (f"Font {name}: width Expects '{height}' "
                   f"found '{cfont.height}'")
            self.assertEqual(height, cfont.height, msg=msg)
            msg = (f"Font {name}: width Expects '{offset}' "
                   f"found '{cfont.offset}'")
            self.assertEqual(offset, cfont.offset, msg=msg)
            msg = (f"Font {name}: width Expects '{numchars}' "
                   f"found '{cfont.numchars}'")
            self.assertEqual(numchars, cfont.numchars, msg=msg)
            msg = (f"Font {name}: width Expects '{nbrows}' "
                   f"found '{cfont.nbrows}'")
            self.assertEqual(nbrows, cfont.nbrows, msg=msg)
            msg = (f"Font {name}: width Expects '{mono_sp}' "
                   f"found '{cfont.mono_sp}'")
            self.assertEqual(mono_sp, cfont.mono_sp, msg=msg)

    #@unittest.skip("Temporary")
    def test_draw_char(self):
        """
        Test that this method correctly draws standard characters
        to the display.
        """
        x = self._tft.display_max_x / 2 # Origin = 0 (88 = 176 / 2)
        y = self._tft.display_max_y / 2 # Origin = 0 (110 = 220 / 2)

        # Test that an exception is raised when a font is not set first.
        with self.assertRaises(TFTException) as cm:
            self._tft.draw_char(x, y, 'A')

        expect_msg = self._tft.ERROR_MSGS.get('STD_FONT')
        found = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found}'"
        self.assertEqual(expect_msg, found, msg=msg)

        # Test normal operation
        tests = (
            #x  y  mono  width filename
            (x, y, True, 12, 'draw_char_00_01.txt'),
            (x, y, False, 11, 'draw_char_00_01.txt'),
            ((x * 2) - 5, y, True, 12, 'draw_char_02_03.txt'),
            ((x * 2) - 5, y, False, 11, 'draw_char_02_03.txt'),
            (x, (y * 2) - 5, True, 12, 'draw_char_04.txt'),
            (x, (y * 2) - 5, False, 11, 'draw_char_05.txt')
            )

        # Test that a character is drawn at the provided coordinates.
        for idx, data in enumerate(tests):
            xx, yy, mono, expected_width, filename = data
            self._tft.set_font(Terminal12x16, mono_sp=mono)
            width = self._tft.draw_char(xx, yy, 'B')
            expect = self._read_data_file(filename)
            self._run_spi_test(expect, 'test_draw_char', idx=idx)
            msg = (f"Expected width on index '{idx}': '{expected_width}' "
                   f"found '{width}'")
            self.assertEqual(expected_width, width, msg=msg)
            self._read_spi_buff('dummy') # Clear the previous data.

    #@unittest.skip("Temporary")
    def test_draw_text(self):
        """
        Test that a string of text is drawn to the display correctly.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2
        st = 'ABC'
        self._tft.set_font(Terminal12x16)
        st_len = len(st)
        expect_currx = x + (st_len * 11) + st_len
        currx = self._tft.draw_text(x, y, st)
        msg = f"Expected cursor x '{expect_currx}' found '{currx}'"

    #@unittest.skip("Temporary")
    def test_get_char_width(self):
        """
        Test that the correct character width in pixels is returned.
        """
        self._tft.set_font(Terminal12x16)
        width = self._tft.get_char_width('B')
        expected_width = 11
        msg = f"Expected width '{expected_width}' found '{width}'"
        self.assertEqual(expected_width, width, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_text_width(self):
        """
        Test that the correct text strint width in pixels is returmed.
        """
        self._tft.set_font(Terminal12x16)
        width = self._tft.get_text_width('ABC')
        expected_width = 33
        msg = f"Expected width '{expected_width}' found '{width}'"
        self.assertEqual(expected_width, width, msg=msg)

    #@unittest.skip("Temporary")
    def test_set_gfx_font(self):
        """
        Test that a GFX font can be set properly.
        """
        self._tft.set_gfx_font(FreeSerifItalic18pt7b)
        bitmap, glyph, first, last, y_advance = FreeSerifItalic18pt7b
        font = {'bitmap': bitmap, 'glyph': glyph, 'first': first,
                'last': last, 'y_advance': y_advance}
        msg_tmp = "Variable {} expect '{}' found '{}'"

        for var, expect_value in font.items():
            found_value = getattr(self._tft._gfx_font, var)
            msg = msg_tmp.format(var, expect_value, found_value)
            self.assertEqual(expect_value, found_value, msg=msg)

    #@unittest.skip("Temporary")
    def test_draw_gfx_char(self):
        """
        Test that a GFX character can be drawn to the display properly.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2
        ch = 'A'

        # Test that an exception is raised when a font is not set first.
        with self.assertRaises(TFTException) as cm:
            self._tft.draw_gfx_char(x, y, ch)

        expect_msg = self._tft.ERROR_MSGS['GFX_FONT']
        found = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found}'"
        self.assertEqual(expect_msg, found, msg=msg)

        # Test that a character is not found in the current font.
        self._tft.set_gfx_font(FreeSansBold10pt7b)

        with self.assertRaises(TFTException) as cm:
            self._tft.draw_gfx_char(x, y, ch)

        expect_msg = self._tft.ERROR_MSGS['GFX_BAD_CH'].format(ch)
        found = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found}'"
        self.assertEqual(expect_msg, found, msg=msg)

        # Test that a character is drawn at the provided coordinates.
        self._tft.set_gfx_font(FreeSerifItalic18pt7b)
        char_width = self._tft.draw_gfx_char(x, y, ch)
        expect = self._read_data_file('draw_gfx_char.txt')
        self._run_spi_test(expect, 'test_draw_gfx_char')
        ch_tmp = ord(ch) - FreeSerifItalic18pt7b[2] # GFXFont.first
        glyph = GFXGlyph(FreeSerifItalic18pt7b[1][ch_tmp]) # GFXFont.glyph
        msg = f"Expect char width '{glyph.x_advance}' found '{char_width}'"
        self.assertEqual(glyph.x_advance, char_width, msg=msg)

    #@unittest.skip("Temporary")
    def test_draw_gfx_text(self):
        """
        Test that a string of text is drawn to the display correctly.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2
        self._tft.set_gfx_font(FreeSerifItalic18pt7b)
        st = 'ABC'
        first = FreeSerifItalic18pt7b[2] # GFXFont.first
        xa = []

        for c in [ord(c) - first for c in st]:
            glyph = GFXGlyph(FreeSerifItalic18pt7b[1][c]) # GFXFont.glyph
            xa.append(glyph.x_advance)

        expect_currx = x + xa[0] + xa[1] + xa[2] + len(st)
        currx = self._tft.draw_gfx_text(x, y, st)
        msg = f"Expected cursor x '{expect_currx}' found '{currx}'"
        self.assertEqual(expect_currx, currx, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_gfx_char_extent(self):
        """
        Test that the proper character extent is returned.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2

        # Test that an exception is raised when a font is not set first.
        with self.assertRaises(TFTException) as cm:
            self._tft.get_gfx_char_extent(x, y, 'A')

        expect_msg = self._tft.ERROR_MSGS.get('GFX_FONT')
        found = str(cm.exception)
        msg = f"Error message expected '{expect_msg}' found '{found}'"
        self.assertEqual(expect_msg, found, msg=msg)
        # Test that an invalid character returns all zeros for gw, gh, and xa.
        self._tft.set_gfx_font(FreeSerifItalic18pt7b)
        ch = '\xFF'
        w, h, xa = self._tft.get_gfx_char_extent(x, y, ch)
        expect_w = expect_h = expect_xa = 0
        msg = (f"Expect w={expect_w}, h={expect_h}, xa={expect_xa} "
               f"found w={w}, h={h}, xa={xa}")
        self.assertEqual(expect_w, w, msg=msg)
        self.assertEqual(expect_h, h, msg=msg)
        self.assertEqual(expect_xa, xa, msg=msg)
        # Test normal character.
        ch = 'C'
        w, h, xa = self._tft.get_gfx_char_extent(x, y, ch)
        ch_tmp = ord(ch) - FreeSerifItalic18pt7b[2] # GFXFont.first
        glyph = GFXGlyph(FreeSerifItalic18pt7b[1][ch_tmp]) # GFXFont.glyph
        expect_w = glyph.width
        expect_h = glyph.height
        expect_xa = glyph.x_advance
        msg = (f"Expect w={expect_w}, h={expect_h}, xa={expect_xa} "
               f"found w={w}, h={h}, xa={xa}")
        self.assertEqual(expect_w, w, msg=msg)
        self.assertEqual(expect_h, h, msg=msg)
        self.assertEqual(expect_xa, xa, msg=msg)

    #@unittest.skip("Temporary")
    def test_get_gfx_text_extent(self):
        """
        Test that the proper text string extent is returned.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2
        st = 'ABC'
        self._tft.set_gfx_font(FreeSerifItalic18pt7b)
        w, h = self._tft.get_gfx_text_extent(x, y, st)
        glyphs = []

        for ch in st:
            # GFXFont.first
            ch_tmp = ord(ch) - FreeSerifItalic18pt7b[2]
            # GFXFont.glyph
            glyphs.append(GFXGlyph(FreeSerifItalic18pt7b[1][ch_tmp]))

        expect_w = sum([g.x_advance for g in glyphs])
        expect_h = max([g.height for g in glyphs])
        msg = f"Expect w={expect_w}, h={expect_h} found w={w}, h={h}"
        self.assertEqual(expect_w, w, msg=msg)
        self.assertEqual(expect_h, h, msg=msg)

    #@unittest.skip("Temporary")
    def test_draw_rectangle(self):
        """
        Test that the correct data is sent to the ILI9225 board.
        """
        x1, y1 = 44, 55
        x2, y2 = 132, 165
        self._tft.draw_rectangle(x1, y1, x2, y2, Colors.LIGHTGREEN)
        expect = self._read_data_file('draw_rectangle.txt')
        self._run_spi_test(expect, 'test_draw_rectangle')

    #@unittest.skip("Temporary")
    def test_fill_rectangle(self):
        """
        Test that a rectangle area is filled with c color.
        """
        x1, y1 = 44, 55
        x2, y2 = 132, 165
        self._tft.fill_rectangle(x1, y1, x2, y2, Colors.LIGHTGREEN)
        expect = self._read_data_file('fill_rectangle.txt')
        self._run_spi_test(expect, 'test_fill_rectangle')

    #@unittest.skip("Temporary")
    def test_draw_circle(self):
        """
        Test that a circle is drawn on the display.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2
        radius = 50
        self._tft.draw_circle(x, y, radius, Colors.BLUE)
        expect = self._read_data_file('draw_circle.txt')
        self._run_spi_test(expect, 'test_draw_circle')

    #@unittest.skip("Temporary")
    def test_fill_circle(self):
        """
        Test that a filled circle is drawn on the display.
        """
        x = self._tft.display_max_x / 2
        y = self._tft.display_max_y / 2
        radius = 50
        self._tft.fill_circle(x, y, radius, Colors.BLUE)
        expect = self._read_data_file('fill_circle.txt')
        self._run_spi_test(expect, 'test_fill_circle')

    #@unittest.skip("Temporary")
    def test_draw_triangle(self):
        """
        Test that a triangle is correctly drawn on the display.
        """
        x0, y0 = 88, 165
        x1, y1 = 44, 55
        x2, y2 = 132, 55
        self._tft.draw_triangle(x0, y0, x1, y1, x2, y2, Colors.RED)
        expect = self._read_data_file('draw_triangle.txt')
        self._run_spi_test(expect, 'test_draw_triangle')

    #@unittest.skip("Temporary")
    def test_fill_triangle(self):
        """
        Test that a filled triangle is correctly drawn on the display.
        """
        tests = (
            #x0, y0,  x1, y1, x2 , y2   look at the code to understand.
            # No swap
            (44, 55, 132, 55, 88, 165, 'fill_triangle_01_03_04.txt'),
            # y0 > y1 swaped first
            (88, 165, 132, 55, 44, 165, 'fill_triangle_02.txt'),
            # y1 > y2 swaped second
            (44, 55, 88, 165, 132, 55, 'fill_triangle_01_03_04.txt'),
            # y0 > y1 and y1 > y2 swapped both
            (88, 165, 132, 55, 44, 55, 'fill_triangle_01_03_04.txt'),
            # Straight line
            (44, 55, 88, 55, 132, 55, 'fill_triangle_05.txt'),
            )

        for corrd in tests:
            self._tft.fill_triangle(*corrd[:-1], Colors.BLUE)
            expect = self._read_data_file(corrd[-1])
            self._run_spi_test(expect, 'test_fill_triangle')
            self._read_spi_buff('dummy') # Clear the previous data.

    #@unittest.skip("Temporary")
    def test_draw_line(self):
        """
        Test that a line is correctly drawn on the display.
        """
        x0, y0 = 88, 75
        x1, y1 = 88, 145
        self._tft.draw_line(x0, y0, x1, y1, Colors.RED)
        expect = self._read_data_file('draw_line.txt')
        self._run_spi_test(expect, 'test_draw_line')

    #@unittest.skip("Temporary")
    def test_draw_pixel(self):
        """
        Test that a pixel is correctly drawn on the display.
        """
        x0, y0 = 88, 75
        self._tft.draw_pixel(x0, y0, Colors.BLUE)
        expect = [
            [self._tft.CMD_RAM_ADDR_SET1, 1, 88],
            [self._tft.CMD_RAM_ADDR_SET2, 1, 75],
            [self._tft.CMD_GRAM_DATA_REG, 1, 31]
            ]
        self._run_spi_test(expect, 'test_draw_pixel')

    ## @unittest.skip("Temporary")
    ## def test_draw_bitmap(self):
    ##     """
    ##     Test that a bitmap image is correctly drawn to the display.
    ##     """
    ##     bitmap = None
    ##     filename = 'lena.bmp'

    ##     with open(f"{self.CURRENT_PATH}/{filename}", 'rb') as f:
    ##         bitmap = f.read()

    ##     self._tft.orientation = 1
    ##     x, y = 0, 0
    ##     self._tft.draw_bitmap(x, y, bitmap, 220, 176, Colors.LIGHTGREY)
    ##     expect = () #self._read_data_file('draw_bitmap.txt')
    ##     self._run_spi_test(expect, 'test_draw_bitmap')

    #@unittest.skip("Temporary")
    def test_rgb16_to_bgr16(self):
        """
        Test that a 16 bit RGB color is correctly converted to a
        16 bit BGR color.
        """
        rgb_blue = Colors.BLUE
        bgr_blue = BGR16BitColor.BLUE
        found_color = self._tft.rgb16_to_bgr16(rgb_blue)
        msg = f"Expect BGR color '{bgr_blue}' found '{found_color}'"
        self.assertEqual(bgr_blue, found_color, msg=msg)

    #@unittest.skip("Temporary")
    def test_rgb24_to_rgb16(self):
        """
        Test that a 24 bit RGB components is correctly converted to a
        16 bit RGB color.
        """
        rgb24_red_red = 0xFF # 24 bit RED component
        rgb24_red_grn = 0x00 # 24 bit GRN component
        rgb24_red_blu = 0x00 # 24 bit BLU component
        rgb16_red = Colors.RED
        found_color = self._tft.rgb24_to_rgb16(
            rgb24_red_red, rgb24_red_grn, rgb24_red_blu)
        msg = f"Expect RGB 16 color '{rgb16_red}' found '{found_color}'"
        self.assertEqual(rgb16_red, found_color, msg=msg)

    #@unittest.skip("Temporary")
    def test_rgb16_to_rgb24(self):
        """
        Test that a 16 bit RGB color is correctly converted to a
        24 bit RGB components.
        """
        rgb16_red = Colors.RED
        rgb24_red_red = 0xFF # 24 bit RED component
        rgb24_red_grn = 0x00 # 24 bit GRN component
        rgb24_red_blu = 0x00 # 24 bit BLU component
        found_components = self._tft.rgb16_to_rgb24(rgb16_red)
        msg = "Expect RGB 24 color  {} component '{}' found '{}'"
        self.assertEqual(rgb24_red_red, found_components[0], msg=msg.format(
            'RED', rgb24_red_red, found_components[0]))
        self.assertEqual(rgb24_red_grn, found_components[1], msg=msg.format(
            'GRN', rgb24_red_grn, found_components[1]))
        self.assertEqual(rgb24_red_blu, found_components[2], msg=msg.format(
            'BLU', rgb24_red_blu, found_components[2]))

    #@unittest.skip("Temporary")
    def test__set_window(self):
        """
        Test that the _set_window() method creates a window to draw in which
        is smaller than the size of the full display.
        """
        tests = ((59, 73, 117, 147),
                 (73, 59, 147, 117),
                 (59, 73, 117, 147),
                 (73, 59, 147, 117))
        expect = [
            [self._tft.CMD_ENTRY_MODE, 1, 4120],
            [self._tft.CMD_HORIZONTAL_WINDOW_ADDR1, 1, 147],
            [self._tft.CMD_HORIZONTAL_WINDOW_ADDR2, 1, 73],
            [self._tft.CMD_VERTICAL_WINDOW_ADDR1, 1, 117],
            [self._tft.CMD_VERTICAL_WINDOW_ADDR2, 1, 59],
            [self._tft.CMD_RAM_ADDR_SET1, 1, 73],
            [self._tft.CMD_RAM_ADDR_SET2, 1, 117],
            [self._tft.CMD_GRAM_DATA_REG, 1, 0x00]
            ]

        for orientation in range(4)[::-1]: # Count backwards
            self._tft.orientation = orientation
            x, y, x1, y1 = tests[orientation]

            for mode in [getattr(AutoIncMode, m)
                         for m in dir(AutoIncMode) if not m.startswith('_')]:
                self._tft._set_window(x, y, x1, y1, mode)
                self._run_spi_test(expect, 'test__set_window')
                self._tft._reset_window()
                self._read_spi_buff('dummy') # Clear the previous data.

    #@unittest.skip("Temporary")
    def test___repr__(self):
        """
        Test that the __repr__ method work correctly.
        """
        rpi_name = self._tft.PLATFORM
        sre = self.REGEX_REPR.search(str(self._tft))
        found = sre.group('platform')
        msg = f"The platform should be '{rpi_name}' found '{found}'"
        self.assertEqual(rpi_name, found, msg=msg)
