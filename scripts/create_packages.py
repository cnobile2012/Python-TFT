#!/usr/bin/env python3
#
# scripts/create_packages.py
#
# This script creates the packages for all platforms.
#

import os
import re
import sys
import curses
from io import StringIO
from shutil import copytree, copy2, ignore_patterns

from curses_file_chooser import FileChooser, ExitData


class CreatePackages:
    """
    Creates packages.
    """
    RX_CLASS_DEF = re.compile(r"^(class) +| +(def) +.*$")
    RX_QUOTES = re.compile(r'^(.+)(?:(""")|(\'\'\').*)$', re.MULTILINE)
    RX_ALL_QUOTES = re.compile(r'^(.+)(?:(""")|(\'\'\')|(")|(\'))(.*)$')
    RX_HASH = re.compile(r"(.*)(#+).*")
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    BUILD_PATH = 'build'
    FONT_PATH = 'fonts'
    ILI9225 = 'ILI9225'
    ILI9341 = 'ILI9341'

    def __init__(self, options):
        self._options = options
        self._fonts = []

    def start(self):
        build_path = os.path.join(self.ROOT_PATH, self.BUILD_PATH)
        if not os.path.lexists(build_path): os.mkdir(build_path)
        ret = False

        if self._options.fonts:
            ed = ExitData()
            path = os.path.join(self.ROOT_PATH, self.FONT_PATH)
            curses.wrapper(FileChooser, path=path, exit_data=ed)
            self._fonts[:] = ed.files
            ret = ed.status

        if not ret:
            if self._options.computer: self._create_computer(build_path)
            if self._options.circuitpython: self._create_circuitpython(
                build_path)
            if self._options.micropython: self._create_micropython(build_path)
            if self._options.raspi: self._create_raspi(build_path)

    def _create_circuitpython(self, build_path):
        platform = 'circuitpython'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages)

    def _create_computer(self, build_path):
        platform = 'computer'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages)

    def _create_micropython(self, build_path):
        platform = 'micropython'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages)

    def _create_raspi(self, build_path):
        platform = 'raspberrypi'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages)

    def _create_paths(self, build_path, platform):
        packages = {}
        path = os.path.join(build_path, platform)
        if not os.path.lexists(path): os.mkdir(path)

        if self._options.ili9225:
            path_package = os.path.join(build_path, path, self.ILI9225)
            packages[self.ILI9225] = path_package
            if not os.path.lexists(path_package): os.mkdir(path_package)

        if self._options.ili9341:
            path_package = os.path.join(build_path, path, self.ILI9341)
            packages[self.ILI9341] = path_package
            if not os.path.lexists(path_package): os.mkdir(path_package)

        return packages

    def _copy_code(self, packages, platform):
        pattern0 = ('__pycache__', 'tests')
        pattern1 = pattern0 + ('__init__.py',)

        for chip, path in packages.items():
            kwargs = {
                'ignore': ignore_patterns(*pattern0),
                'dirs_exist_ok': True
                }
            # Copy chip path
            src = os.path.join(self.ROOT_PATH, chip)
            copytree(src, path, **kwargs)

            # Copy font files
            for f in self._fonts:
                src = os.path.join(self.ROOT_PATH, self.FONT_PATH, f)
                dst = os.path.join(path, self.FONT_PATH)
                if not os.path.lexists(dst): os.mkdir(dst)
                copy2(src, dst)

            # Copy utils path
            kwargs['ignore'] = ignore_patterns(*pattern1)
            src = os.path.join(self.ROOT_PATH, 'utils')
            copytree(src, path, **kwargs)
            # Copy platform file
            src = f'py_versions/{platform}.py'
            copy2(src, path)

    def _fix_ili9225(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _fix_ili9341(self, process_path):
        pass

    def _fix_init(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _fix_compatibility(self, process_path):
        fix = "from py_versions."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _fix_circuitpython(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _fix_computer(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _fix_micropython(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _fix_raspberrypi(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def __fix_imports(self, process_path, fix, change):
        if self._options.debug: sys.stdout.write('\n' + process_path + '\n')

        with StringIO() as buff:
            with open(process_path, 'r') as f:
                for line in f:
                    if fix in line:
                        line = line.replace(fix, change)
                        if self._options.debug: sys.stdout.write(line)

                    buff.write(line)

            if not self._options.noop:
                with open(process_path, 'w') as f:
                    f.write(buff.getvalue())

    FIX_FILES = (
        ('ili9225.py', _fix_ili9225, ILI9225),
        ('ili9341.py', _fix_ili9341, ILI9341),
        ('__init__.py', _fix_init, None),
        ('compatibility.py', _fix_compatibility, None),
        ('common.py', None, None),
        ('circuitpython.py', _fix_circuitpython, None),
        ('computer.py', _fix_computer, None),
        ('default_fonts.py', None, None),
        ('micropython.py', _fix_micropython, None),
        ('raspberrypi.py', _fix_raspberrypi, None),
        ('fonts', None, None),
        )

    def _fix_files(self, packages):
        for src, path in packages.items():
            for pyfile, fix, mcu in self.FIX_FILES:
                if (src == self.ILI9225 in (mcu, None)
                    or src == self.ILI9341 in (mcu, None)
                    or mcu == None):
                    process_path = os.path.join(path, pyfile)

                    # Check that the file exists in cases of
                    # non platform specific files.
                    if not os.path.exists(process_path):
                        continue
                else:
                    continue

                if fix is not None:
                    fix(self, process_path)

                if (self._options.force or (
                    self._options.strip and (self._options.circuitpython
                                             or self._options.micropython))):
                    self._strip_doc_strings(process_path)
                    self._strip_comments(process_path)

    def _strip_doc_strings(self, process_path):
        if self._options.debug: sys.stdout.write(f"{process_path}")

        with StringIO() as buff:
            if os.path.isdir(process_path): # Font files
                for f in self._fonts:
                    path = os.path.join(process_path, f)
                    self.__strip_doc_strings(buff, path)
                    self._write_file(buff, path)
                    #buff.truncate(0)
            else:
                self.__strip_doc_strings(buff, process_path)
                self._write_file(buff, process_path)
                #buff.truncate(0)

    def __strip_doc_strings(self, buff, process_path):
        with open(process_path, 'r') as f:
            save_lines = ""
            def_flag = False
            line_flag = False
            pre_flag = False

            for idx, line in enumerate(f, start=1):
                sre = self.RX_CLASS_DEF.search(line)

                if sre:
                    def_flag = True
                else:
                    save_lines += line
                    quotes = self.RX_QUOTES.findall(save_lines)

                    if quotes and any([True for c in quotes[0][0]
                                       if c != ' ']):
                        pre_flag = True

                    if (not pre_flag and def_flag
                        and quotes and len(quotes) == 1):
                        line_flag = True

                        if self._options.debug:
                            sys.stdout.write(f"{idx:>4d} {line}")

                        continue
                    elif (not pre_flag and def_flag and line_flag
                          and quotes and len(quotes) == 2):
                        save_lines = ""
                        def_flag = line_flag = False

                        if self._options.debug:
                            sys.stdout.write(f"{idx:>4d} {line}")

                        continue
                    elif pre_flag and quotes and len(quotes) == 2:
                        pre_flag = False
                        save_lines = ""

                buff.write(line)

    def _strip_comments(self, process_path):
        if self._options.debug: sys.stdout.write(f"{process_path}")

        with StringIO() as buff:
            if os.path.isdir(process_path): # Font files
                for f in self._fonts:
                    path = os.path.join(process_path, f)
                    self.__strip_comments(buff, path)
                    self._write_file(buff, path)
                    #buff.truncate(0)
            else:
                self.__strip_comments(buff, process_path)
                self._write_file(buff, process_path)
                #buff.truncate(0)

    def __strip_comments(self, buff, process_path):
        with open(process_path, 'r') as f:
            save_lines = ""
            quote_flag = False
            code_flag = False
            hash_flag = False
            mult_hash_flag = False

            for idx, line in enumerate(f, start=1):
                quote = self.RX_ALL_QUOTES.search(line)

                if quote:
                    save_lines += line
                    quote_flag = True

                hash_data = self.RX_HASH.search(line)

                if hash_data:
                    groups = hash_data.groups()
                    code_flag = any([True for c in groups[0] if c != ' '])
                    hash_flag = '#' in groups[1]
                    mult_hash_flag = [True for group in groups
                                      if '#' in group].count(True) > 1

                    if (hash_flag and mult_hash_flag
                        and any([True for c in groups[0] if c != ' '])):
                        hash_flag = False
                        mult_hash_flag = False

                        if self._options.debug:
                            sys.stdout.write(f"{idx:>4d} {line}")

                        continue
                    elif not quote_flag and hash_flag and code_flag:
                        line = line[:line.index('#')].rstrip() + '\n'
                        hash_flag = False
                        code_flag = False

                        if self._options.debug:
                            sys.stdout.write(f"{idx:>4d} {line}")
                    elif not (quote_flag and code_flag) and hash_flag:
                        if self._options.debug:
                            sys.stdout.write(f"{idx:>4d} {line}")

                        continue
                    elif quote_flag:
                        quote_count = (save_lines.count('"""')
                                       or save_lines.count("'''"))

                        if quote_count == 2:
                            quote_flag = False

                buff.write(line)

    def _write_file(self, buff, process_path):
        if not self._options.noop:
            with open(process_path, 'w') as f:
                f.write(buff.getvalue().lstrip())


if __name__ == '__main__':
    import traceback
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description=("Creating packages..."))
    parser.add_argument(
        '-a', '--all', action='store_true', default=False,
        dest='all', help="Create all packages."
        )
    parser.add_argument(
        '-c', '--circuitpython', action='store_true', default=False,
        dest='circuitpython', help="Create a CircuitPython package."
        )
    parser.add_argument(
        '-p', '--computer', action='store_true', default=False,
        dest='computer', help="Create a Computer package."
        )
    parser.add_argument(
        '-m', '--micropython', action='store_true', default=False,
        dest='micropython', help="Create a MicroPython package."
        )
    parser.add_argument(
        '-r', '--raspi', action='store_true', default=False,
        dest='raspi', help="Create a Raspberry Pi package."
        )
    parser.add_argument(
        '-2', '--ili9225', action='store_true', default=False,
        dest='ili9225', help="Create a ILI9225 package."
        )
    parser.add_argument(
        '-3', '--ili9341', action='store_true', default=False,
        dest='ili9341', help="Create a ILI9341 package."
        )
    parser.add_argument(
        '-s', '--strip', action='store_true', default=False,
        dest='strip', help=("Strip comments and non-code white space no "
                            "the MicroPython and CircuitPython packages.")
        )
    parser.add_argument(
        '-f', '--force-strip', action='store_true', default=False,
        dest='force', help=("Force striping on all packages including "
                            "the Raspberry Pi and Computer packages.")
        )
    parser.add_argument(
        '-F', '--fonts', action='store_true', default=False, dest='fonts',
        help="Choose which fonts to put in the final packages."
        )
    parser.add_argument(
        '-D', '--debug', action='store_true', default=False, dest='debug',
        help="Run in debug mode."
        )
    parser.add_argument(
        '-N', '--noop', action='store_true', default=False, dest='noop',
        help="Run as if creating, but do nothing."
        )
    options = parser.parse_args()
    exit_val = 0

    if options.debug:
        sys.stdout.write(f"DEBUG--options: {options}\n")

    if options.all:
        options.computer = True
        options.circuitpython = True
        options.micropython = True
        options.raspi = True
        options.ili9225 = True
        options.ili9341 = True

    if options.ili9225 or options.ili9341:
        try:
            cp = CreatePackages(options)
            cp.start()
        except Exception as e:
            tb = sys.exc_info()[2]
            traceback.print_tb(tb)
            sys.stdout.write(f"{sys.exc_info()[0]}: {sys.exc_info()[1]}\n")
            exit_val = 1
    else:
        exit_val = 2
        parser.print_help()
        sys.stdout.write("At least one or both ILI9225 or ILI9341 "
                         "must be chosen.\n")

    sys.exit(exit_val)
