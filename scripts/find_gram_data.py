#!/bin/env python
#
#

import os
import re
import sys
from io import StringIO

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_PATH)

from ILI9225 import ILI9225


REG_EX = re.compile(r"(self._tft\.\w+), ([ ,\w]+)")


if len(sys.argv) > 1:
    filename = sys.argv[1]

    with open(filename, 'r') as f:
        result = f.read()
else:
    head, tail = os.path.split(sys.argv[0])
    print(f"{tail}: A file path must be the 1st argument.")
    sys.exit(1)


cmd_list = []
items = REG_EX.findall(result.replace("\n", "").replace("   ", ""))

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

total = len(cmd_list)
print(f"Total: {total}\nStates {cmd_list}")
sys.exit(0)
