#!/usr/bin/env python3

import re
import sys
from io import StringIO


RX_CLASS_DEF = re.compile(r"^(class) +| +(def) +.*$")
RX_QUOTES = re.compile(r'^(.+)(?:(""")|(\'\'\'))(.*)$', re.MULTILINE)
RX_ALL_QUOTES = re.compile(r'^(.+)(?:(""")|(\'\'\')|(")|(\'))(.*)$')
RX_HASH = re.compile(r"(.*)(#+).*")

filepath = "scripts/test_strip.txt"


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

                    if quotes and any([True for c in quotes[0][0]
                                       if c != ' ']):
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
            save_lines = ""
            quote_flag = False
            code_flag = False
            hash_flag = False
            mult_hash_flag = False

            for idx, line in enumerate(f, start=1):
                quote = RX_ALL_QUOTES.search(line)

                if quote:
                    save_lines += line
                    quote_flag = True

                hash_data = RX_HASH.search(line)

                if hash_data:
                    groups = hash_data.groups()
                    code_flag = any([True for c in groups[0] if c != ' '])
                    hash_flag = '#' in groups[1]
                    mult_hash_flag = [True for group in groups
                                      if '#' in group].count(True) > 1

                    if (hash_flag and mult_hash_flag
                        and any([True for c in groups[0] if c != ' '])):
                        print("if 01", groups, quote_flag, code_flag,
                              hash_flag, mult_hash_flag, idx)
                        hash_flag = False
                        mult_hash_flag = False
                        continue
                    elif not quote_flag and hash_flag and code_flag:
                        line = line[:line.index('#')].rstrip() + '\n'
                        print("if 02", groups, quote_flag, code_flag,
                              hash_flag, mult_hash_flag, idx)
                        hash_flag = False
                        code_flag = False
                    elif not (quote_flag and code_flag) and hash_flag:
                        print("if 03", groups, quote_flag, code_flag,
                              hash_flag, mult_hash_flag, idx)
                        continue
                    elif quote_flag:
                        quote_count = (save_lines.count('"""')
                                       or save_lines.count("'''"))
                        print("if 04", groups, quote_flag, code_flag,
                              hash_flag, mult_hash_flag, idx)

                        if quote_count == 2:
                            quote_flag = False

                buff.write(line)

            data = buff.getvalue().lstrip()

    return data


data = strip_doc_strings(filepath)
sys.stdout.write(data)
data = strip_comments(data)
sys.stdout.write(data)
