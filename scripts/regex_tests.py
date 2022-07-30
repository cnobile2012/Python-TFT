#!/usr/bin/env python

import re

string0 = '    src = "# is used in code so keep it."'
string1 = '    self.hash_code = "Test a hash # some comment "'
string2 = '    self.brightness = brightness # Default it maximum brightness.'
string3 = '    0x06, 0x00, 0x24, 0x7E, 0x24, 0x7E, 0x24,  # Code for char #'
string4 = '    MODE_BOTTOM_UP_L2R, MODE_L2R_BOTTOM_UP) # 270°'
string5 = '    # POOP'
string6 = '        duh = """'
string7 = '        """'
string8 = '''"""
        Set a standard font.
        :param font: A parsed font object.
        :type font: tuple
        """'''
string9 = '''        duh = """
        This # needs to stay
        # So does this one
        """'''
string10 = "        0xA8, # '''"

test0 = (string0, string1, string2, string3, string4)
test1 = (string5,)
test2 = (string6, string7, string8, string9, string10)

RX_HASH_CODE = r'^(?:.+= +|.+,+)("|\')?[^#]*(#*)?[^"|\']+("|\'")?.*$'
RX_1ST_HASH = r'^ *(#+)?.*$'
RX_QUOTES = r'^ *(#*)(.*)("{3}|\'{3}).*$'

for s in test0:
    result = re.search(RX_HASH_CODE, s)
    print(f"{str(result.groups()):<18}: {s}")

for s in test1:
    result = re.search(RX_1ST_HASH, s)
    print(f"{str(result.groups()):<18}: {s}")

for s in test2:
    result = re.search(RX_QUOTES, s, re.MULTILINE)
    print(f"{str(result.groups()):<18}: {s}")
