#!/usr/bin/env python3
#
# scripts/create_packages.py
#
# This script creates the packages for all platforms.
#

import os
import re
import sys
from io import StringIO
from shutil import copytree, copy2, ignore_patterns


class CreatePackages:
    """
    Creates packages.
    """
    RX_CLASS_DEF = re.compile(r"^ *(class)|(def).*$", re.MULTILINE)
    RX_QUOTES = re.compile(r'^ +(""")|(\'\'\').*$', re.MULTILINE)
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    BUILD_PATH = 'build'
    ILI9225 = 'ILI9225'
    ILI9341 = 'ILI9341'

    def __init__(self, options):
        self._options = options

    def start(self):
        build_path = os.path.join(self.ROOT_PATH, self.BUILD_PATH)
        if not os.path.lexists(build_path): os.mkdir(build_path)
        if self._options.computer: self._create_computer(build_path)
        if self._options.circuitpython: self._create_circuitpython(build_path)
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

        for src, path in packages.items():
            kwargs = {
                'ignore': ignore_patterns(*pattern0),
                'dirs_exist_ok': True
                }
            copytree(src, path, **kwargs)
            src = 'fonts'
            dst = os.path.join(path, src)
            copytree(src, dst, **kwargs)
            kwargs['ignore'] = ignore_patterns(*pattern1)
            src = 'utils'
            copytree(src, path, **kwargs)
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
        if self._options.debug: sys.stderr.write('\n' + process_path + '\n')

        with StringIO() as buff:
            with open(process_path, 'r') as f:
                for line in f:
                    if fix in line:
                        line = line.replace(fix, change)
                        if self._options.debug: sys.stderr.write(line)

                    buff.write(line)

            if not self._options.noop:
                with open(process_path, 'w') as f:
                    f.write(buff.getvalue())

    def _strip_doc_strings(self, process_path):
        with StringIO() as buff:
            with open(process_path, 'r') as f:
                save_lines = ""

                for idx, line in enumerate(f, start=1):
                    sre = self.RX_CLASS_DEF.search(line)
                    print(save_lines)

                    if sre:
                        save_lines = line
                        print('class or def', idx)
                    else:
                        save_lines += line
                        quotes = self.RX_QUOTES.findall(save_lines)

                        if quotes or len(save_lines) > 0:
                            if self._options.debug: sys.stderr.write(line)
#                            print('first or between', idx)
                            continue
                        elif quotes and len(quotes) > 1:
                            save_lines = ""
                            if self._options.debug: sys.stderr.write(line)
#                            print('last', idx)
                            continue

                    buff.write(line)

            if not self._options.noop:
                with open(process_path, 'w') as f:
                    f.write(buff.getvalue())

    def _strip_comments(self, process_path):
        pass


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
        )

    def _fix_files(self, packages):
        for src, path in packages.items():
            for pyfile, fix, mcu in self.FIX_FILES:
                if (src == self.ILI9225 in (mcu, None)
                    or src == self.ILI9341 in (mcu, None)):
                    process_path = os.path.join(path, pyfile)
                else:
                    continue

                if fix is not None:
                    fix(self, process_path)

                if (self._options.force or (
                    self._options.strip and (self._options.circuitpython
                                             or self._options.micropython))):
                    self._strip_doc_strings(process_path)
                    #self._strip_comments(process_path)

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
        sys.stderr.write(f"DEBUG--options: {options}\n")

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
            sys.stderr.write(f"{sys.exc_info()[0]}: {sys.exc_info()[1]}\n")
            exit_val = 1
    else:
        exit_val = 2
        parser.print_help()
        sys.stderr.write("At least one or both ILI9225 or ILI9341 "
                         "must be chosen.\n")

    sys.exit(exit_val)
