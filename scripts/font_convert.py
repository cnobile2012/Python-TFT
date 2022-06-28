#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This app converts Adafruit type font files to a python file that can
be used with the display library.
"""

import io
import os
import glob
import re


class FontConvert:
    """
    This class converts Adafruit type font files to a python file that can
    be used with the display library.
    """
    # const uint8_t TomThumbBitmaps[] PROGMEM = {
    _REGEX_UINT8_T = re.compile(
        r'^const +uint8_t +(\w+) *\[\] +PROGMEM *= *{ *$')
    # const GFXglyph TomThumbGlyphs[] PROGMEM = {
    _REGEX_GLYPH = re.compile(
        r'^const +GFXglyph +(\w+) *\[\] +PROGMEM *= *{ *$')

    _REGEX_DEFINE = re.compile(r'^#define +(\w+)? +(\d+) *$')
    _REGEX_CONN = re.compile(r'^#if +\( *(\w+)? *\) *$')
    _REGEX_END = re.compile(r'^#endif +.+?\( *(\w+)? *\) *$')
    _REGEX_FONT = re.compile(r'^const +GFXfont +(\w+) +PROGMEM.+$')
    _REGEX_0X = re.compile(r'^ *(0[xX].+)$')
    _REGEX_ARRAY = re.compile(r'^ *(\[.+)$')

    def __init__(self, options):
        self._options = options

    def start(self):
        c_files = self._get_c_file_list()

        if len(c_files) > 0:
            self._convert_files(c_files)
        else:
            print("There were no files to convert "
                  "in path {}".format(self._options.c_font))

    def _get_c_file_list(self):
        path_list = []
        path = "{}{}{}".format(self._options.c_font[0],
                               os.sep, self._options.c_font[1])

        if os.path.isfile(path):
            path_list.append(path)
        elif os.path.isdir(path):
            files = os.path.abspath("{}{}*.h".format(path, os.sep))
            path_list[:] = [f for f in glob.glob(files)]

        if self._options.debug:
            print("File list: {}".format(path_list))

        return path_list

    def _convert_files(self, c_files):
        for f in c_files:
            data = self._parse_file(f)

            if not self._options.noop and data:
                if self._options.py_font[1].endswith(".py"):
                    path = "{}{}{}".format(self._options.py_font[0], os.sep,
                                           self._options.py_font[1])
                else:
                    path = "{}{}{}".format(
                        self._options.py_font[0], os.sep,
                        os.path.basename(f).replace('.h', '.py'))

                    if not self._options.noop:
                        self._save_file(path, data)

    def _parse_file(self, file):
        data = io.StringIO()

        with open(file, 'r') as f:
            var_name = None

            while True:
                text = f.readline()
                if text == "": break
                text = text.replace('\r\n', '\n')
                text = text.replace('//', '#')
                text = text.replace('/*', '#').replace('*/', '')
                text = text.replace('*', '#')
                text = text.replace('}; ', ']  ').replace(';', '')
                text = text.replace(' \n', '\n')

                if 'PROGMEM' in text:
                    groups = self._REGEX_UINT8_T.search(text)

                    if groups:
                        var_name = groups.groups()[0]
                        text = "{} = [\n".format(var_name)

                    groups = self._REGEX_GLYPH.search(text)

                    if groups:
                        var_name = groups.groups()[0]
                        text = "{} = [\n".format(var_name)
                else:
                    text = text.replace('{', '[').replace('}', ']')

                groups = self._REGEX_FONT.search(text)
                if groups: text = "{} = [\n".format(*groups.groups())

                text = text.replace('(uint8_t  #)', '  ')
                text = text.replace('(GFXglyph #)', '  ')
                text = text.replace('{', '[')

                # Process with conditionals
                groups = self._REGEX_DEFINE.search(text)
                if groups: text = '{} = {}\n'.format(*groups.groups())

                groups = self._REGEX_CONN.search(text)
                if groups: text = ']\n\nif {}:\n    {} += [\n'.format(
                    groups.groups()[0], var_name)

                groups = self._REGEX_END.search(text)
                if groups: text = '# end {}\n'.format(*groups.groups())

                # Some clean up
                groups = self._REGEX_0X.search(text)
                if groups: text = "    {}\n".format(*groups.groups())

                groups = self._REGEX_ARRAY.search(text)
                if groups: text = "    {}\n".format(*groups.groups())

                data.write(text)

        out = data.getvalue()
        data.close()

        if self._options.debug:
            print("data: {}".format(out))

        return out

    def _save_file(self, path, data):
        with open(path, 'w') as f:
            f.write(data)


if __name__ == '__main__':
    import sys
    import traceback
    import argparse

    def find_path(fullpath):
        fullpath = fullpath.strip()
        splitpath = os.path.split(fullpath)
        splitpath = ['.', ''] if splitpath[1] == '.' else list(splitpath)
        splitpath[0] = os.path.abspath(splitpath[0])
        return splitpath

    parser = argparse.ArgumentParser(
        description=("Font convertion..."))
    parser.add_argument(
        '-D', '--debug', action='store_true', default=False, dest='debug',
        help="Run in debug mode.")
    parser.add_argument(
        '-n', '--noop', action='store_true', default=False, dest='noop',
        help="Run as if converting, but do nothing.")
    parser.add_argument(
        '-c', '--c_font', type=str, default='', dest='c_font',
        help="The Adafruit C header font file or path.")
    parser.add_argument(
        '-p', '--py_font', type=str, default='', dest='py_font',
        help="The python font file or path.")
    options = parser.parse_args()
    #print "Options: {}".format(options)

    if not (options.c_font or options.py_font):
        print("Both the C font header and the python file paths "
              "must be provided.")
        parser.print_help()
        sys.exit(1)

    c_path = find_path(options.c_font)
    if '.h' not in c_path[1]: c_path = ["{}{}{}".format(
        c_path[0], os.sep, c_path[1]), '']
    py_path = find_path(options.py_font)

    if options.debug:
        sys.stderr.write("DEBUG--options: {}\n".format(options))
        sys.stderr.write("DEBUG--c_path {}, py_path {}\n".format(
            c_path, py_path ))

    if not os.path.exists(options.c_font):
        print("The '{}' path does not exist.".format(options.c_font))
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(py_path[0]):
        print("The '{}' path does not exist.".format(options.py_font))
        parser.print_help()
        sys.exit(1)

    if py_path[1].endswith('.py') and not c_path[1].endswith('.h'):
        print("The 'c_font' path must point to a file if the 'py_font' "
              "path is a file.")

    options.c_font = c_path
    options.py_font = py_path

    try:
        fc = FontConvert(options)
        fc.start()
    except Exception as e:
        tb = sys.exc_info()[2]
        traceback.print_tb(tb)
        print("{}: {}".format(sys.exc_info()[0], sys.exc_info()[1]))
        sys.exit(1)

    sys.exit(0)
