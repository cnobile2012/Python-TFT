#!/usr/bin/env python3

import re
import sys
from io import StringIO


RX_CLASS_DEF = re.compile(r"^(class) +| +(def) +.*$")
RX_QUOTES = re.compile(r'^(?: *)(#*).*("{3}|\'{3})(?:.*)$', re.MULTILINE)
RX_1ST_HASH = re.compile(r'^ *(#+)?.*$')
RX_HASH_CODE = re.compile(r'^(?:.+= +|.+,+)("|\')?[^#.]*(#*)?'
                          r'[^"|\']+("|\'")?.*$')

filepath = "scripts/test_strip.py"


def strip_doc_strings(process_path):
    data = ""

    with StringIO() as buff:
        with open(process_path, 'r') as f:
            save_lines = ""
            def_flag = False
            quote_flag = False
            pre_flag = False

            for idx, line in enumerate(f, start=1):
                #print("FLAGS", def_flag, quote_flag, pre_flag)
                sre = RX_CLASS_DEF.search(line)

                if sre:
                    def_flag = True
                else:
                    save_lines += line
                    quotes = RX_QUOTES.findall(save_lines)

                    if quotes and any([True for c in quotes[0][0] if c != ' ']):
                        pre_flag = True

                    #print("After findall()", quotes, idx)

                    if (not pre_flag and def_flag
                        and quotes and len(quotes) == 1):
                        quote_flag = True
                        #print('first or between', quote_flag, idx)
                        continue
                    elif (not pre_flag and def_flag and quote_flag
                          and quotes and len(quotes) == 2):
                        save_lines = ""
                        def_flag = quote_flag = False
                        #print('last', quote_flag)
                        continue
                    elif pre_flag and quotes and len(quotes) == 2:
                        pre_flag = False
                        save_lines = ""

                buff.write(line)

            data = buff.getvalue().lstrip()

    return data


def strip_comments(data):
    with StringIO() as buff:
        with StringIO(data) as f:
            quote_flag = False

            for idx, line in enumerate(f, start=1):
                # If a triple quote is found store the lines until the next
                # triple quote is found.
                sre = RX_QUOTES.search(line)

                # Do not process further
                if sre and '#' not in sre.groups()[0] and not quote_flag:
                    quote_flag = True
                elif sre and quote_flag: # Do not process further
                    quote_flag = False
                elif quote_flag: # Do not process further
                    pass
                else:
                    # Handle line where 1st non-space character is a #
                    sre = RX_1ST_HASH.search(line)

                    if sre and sre.groups()[0] is not None:
                        continue

                    # Handle line where there is code followed by a #
                    sre = RX_HASH_CODE.search(line)
                    #if sre: print(sre.groups())

                    if sre and '#' in sre.groups()[1] and (
                        sre.groups()[0] is None or sre.groups()[2] is None):
                            #print(sre.groups(), line)
                            line = line[:line.index('#')].rstrip() + '\n'

                buff.write(line)

            out = buff.getvalue().lstrip()

    return out


data = strip_doc_strings(filepath)
#sys.stdout.write(data)
#sys.stdout.write('\n')
data = strip_comments(data)
sys.stdout.write(data)
