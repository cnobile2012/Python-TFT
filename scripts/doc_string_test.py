#!/usr/bin/env python3

import re
import sys
from io import StringIO


RX_QUOTES = re.compile(r'^ *(#*)(.*)("{3}|\'{3}).*$')
RX_1ST_HASH = re.compile(r'^ *(#+)?.*$')
RX_HASH_CODE = re.compile(r'^(?:.+= +|.+,+)("|\')?[^#]*(#*)?'
                          r'[^"|\']+("|\'")?.*$')

filepath = "scripts/test_strip.py"
#filepath = "ILI9225/ili9225.py"


def strip_doc_strings(process_path):
    """
    Truth Table

    +----------------------------------------------------+
    | nm |  lb   | code  | quote | lb    | quote | code  |
    |    |       |       |       | _code | _flag | _flag |
    |====|=======|=======|=======|=======|=======|=======|
    | 1  | True  | X     | X     | False | X     | X     |
    | 2  | False | X     | X     | True  | X     | X     |
    | 3  | False | True  | X     |       | X     | False |
    | 4  | False | True  | True  |       | X     | True  |
    | 5  | False | False | True  |       | True  | X     |
    | 6  | False | False | True  |       | False | False |
    | 7  | X     | X     | X     |       | True  | X     |
    +----------------------------------------------------+

    .. note::
       1. If lb exists pass through
       2. If lb_code exists pass through
       3. Pass through, Set code_flag
       4. Pass through, Unset code_flag
       5. Continue, Unset quote_flag
       6. Continue, Set quote_flag
       7. Continue
       False: Must not be set or exist in RX.
       True : Must be set or exist in RX.
       X    : Does not matter
    """
    data = ""

    with StringIO() as buff:
        with open(process_path, 'r') as f:
            quote_flag = False
            code_flag = False

            for idx, line in enumerate(f, start=1):
                sre = RX_QUOTES.search(line)

                if sre:
                    lb, code, quote = sre.groups()
                    lb = '#' in lb
                    code = len(code) > 0
                    quote = '"""' == quote.replace("'''", '"""')
                    lb_code = '#' in sre.groups()[1]
                    ## print(f"lb: {str(lb):<5}, code: {str(code):<5}, "
                    ##       f"quote: {str(quote):<5}, "
                    ##       f"lb_code: {str(lb_code):<5}, "
                    ##       f"quote_flag: {str(quote_flag):<5}, "
                    ##       f"code_flag: {str(code_flag):<5}, "
                    ##       f"line: {line}", end='')
                    ## print(not lb and not code and quote, sre.groups())

                    if not lb and not lb_code:                      # 1 & 2
                        if code and not code_flag: code_flag = True # 3

                        if not code and quote and code_flag:        # 4
                            code_flag = False
                        elif not code and quote and quote_flag:     # 5
                            quote_flag = False
                            continue
                        elif not code and quote and not code_flag:  # 6
                            quote_flag = True
                            continue
                elif quote_flag:                                    # 7
                    continue

                buff.write(line)

            data = buff.getvalue().lstrip()

    return data


def strip_comments(data):
    """
    Truth Table

    """
    with StringIO() as buff:
        with StringIO(data) as f:
            quote_flag = False
            code_flag = False

            for idx, line in enumerate(f, start=1):
                sre = RX_QUOTES.search(line)

                if sre:
                    lb, code, quote = sre.groups()
                    lb = '#' in lb
                    code = len(code) > 0
                    lb_code = '#' in sre.groups()[1]
                    quote = '"""' == quote.replace("'''", '"""')
                    ## print(f"lb: {str(lb):<5}, code: {str(code):<5}, "
                    ##       f"lb_code: {str(lb_code):<5}, "
                    ##       f"quote: {str(quote):<5}, "
                    ##       f"quote_flag: {str(quote_flag):<5}, "
                    ##       #f"code_flag: {str(code_flag):<5}, "
                    ##       f"line: {line}", end='')
                    ## print(not lb and not code and quote, sre.groups())

                    if not lb and code and not lb_code and not code_flag:
                        code_flag = True

                    if not code and quote and code_flag:
                        code_flag = False
                    elif not lb and not code and quote:
                        quote_flag = True
                    elif not lb and not code and quote_flag:
                        quote_flag = False
                elif quote_flag: # Do not process further
                    pass

                # Handle line where 1st non-space character is a #
                sre = RX_1ST_HASH.search(line)

                if sre:
                    lb1st = sre.groups()[0]
                    lb1st = lb1st is not None and '#' in lb1st
                    if lb1st and not quote_flag and not code_flag: continue
                    #print(lb1st, quote_flag, code_flag, sre.groups(), line)

                # Handle line where there is code followed by a #
                sre = RX_HASH_CODE.search(line)

                if sre:
                    lsdq, hlb, rsdq = sre.groups()
                    lsdq = (False if lsdq is None
                            else '"' == lsdq.replace("'", '"'))
                    hlb = '#' in hlb
                    rsdq = (False if rsdq is None
                            else '"' == rsdq.replace("'", '"'))
                    #print(lsdq, hlb, rsdq, sre.groups(), line)

                    if hlb and (not lsdq or not rsdq):
                        line = line[:line.index('#')].rstrip() + '\n'

                buff.write(line)

            out = buff.getvalue().lstrip()

    return out


data = strip_doc_strings(filepath)
#sys.stdout.write(data)
#sys.stdout.write('\n')
data = strip_comments(data)
sys.stdout.write(data)
