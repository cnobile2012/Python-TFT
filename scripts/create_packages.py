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
    # Removing quotes and # comments
    RX_QUOTES = re.compile(r'^ *(#*)(.*)("{3}|\'{3}).*$')
    RX_1ST_HASH = re.compile(r'^ *(#+)?.*$')
    RX_HASH_CODE = re.compile(r'^(?:.+= +|.+,+)("|\')?[^#]*(#*)?'
                              r'[^"|\']+("|\'")?.*$')
    # Pathing
    RX_LF = re.compile(r'^\n$', re.DOTALL)
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    BUILD_PATH = os.path.join(ROOT_PATH, 'build')
    FONT_DIR = 'fonts'
    UTILS_DIR = 'utils'
    PY_VER_DIR = 'py_versions'
    ILI9225 = 'ILI9225'
    ILI9341 = 'ILI9341'
    # Misc
    STRIP_PLATFORMS = ('circuitpython', 'micropython')
    M_COMPRESS = [
        ('x86', "32 bit"),
        ('x64', "64 bit x86"),
        ('armv6', "ARM Thumb, eg Cortex"),
        ('armv6m', "ARM Thumb, eg Cortex-M0"),
        ('armv7m', "ARM Thumb 2, eg Cortex-M3"),
        ('armv7em', ""),
        ('armv7emsp',
         "ARM Thumb 2, single precision float, eg Cortex-M4F, Cortex-M7"),
        ('armv7emdp', "ARM Thumb 2, double precision float, eg Cortex-M7"),
        ('xtensa', "non-windowed, eg ESP8266"),
        ('xtensawin', "windowed with window size 8, eg ESP32")
        ]
    M_COMPRESS.sort()
    M_COMPRESS.insert(0, ('no arch', "Compress with no architecture assigned"))
    M_COMPRESS.insert(0, ('none', "No compression"))

    def __init__(self, options):
        self._options = options
        self._fonts = []

    def start(self):
        if self._options.compress_list:
            [sys.stdout.write(f"{idx: >2}. {arch: <10} {desc}\n")
             for idx, (arch, desc) in enumerate(self.M_COMPRESS, start=-1)]
        else:
            ret = False

            if self._options.fonts:
                ed = ExitData()
                path = os.path.join(self.ROOT_PATH, self.FONT_DIR)
                curses.wrapper(FileChooser, path=path, exit_data=ed)
                self._fonts[:] = ed.files + ['__init__.py']
                ret = ed.status

            if not ret:
                if not os.path.lexists(self.BUILD_PATH):
                    os.mkdir(self.BUILD_PATH)

                if self._options.computer:
                    self._create_computer(self.BUILD_PATH)

                if self._options.circuitpython:
                    self._create_circuitpython(self.BUILD_PATH)

                if self._options.micropython:
                    self._create_micropython(self.BUILD_PATH)

                if self._options.raspberrypi:
                    self._create_raspi(self.BUILD_PATH)

    def _create_circuitpython(self, build_path):
        platform = 'circuitpython'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages, platform)

    def _create_computer(self, build_path):
        platform = 'computer'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages, platform)

    def _create_micropython(self, build_path):
        platform = 'micropython'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages, platform)

    def _create_raspi(self, build_path):
        platform = 'raspberrypi'
        packages = self._create_paths(build_path, platform)
        self._copy_code(packages, platform)
        self._fix_files(packages, platform)

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
            # Both MicroPython and CircuitPython do not handle
            # __init__.py file properly.
            if platform in self.STRIP_PLATFORMS:
                pattern = pattern1
            else:
                pattern = pattern0

            kwargs = {
                'ignore': ignore_patterns(*pattern),
                'dirs_exist_ok': True
                }
            # Copy chip path
            src = os.path.join(self.ROOT_PATH, chip)
            copytree(src, path, **kwargs)

            if platform in self.STRIP_PLATFORMS:
                with open(os.path.join(path, '__init__.py'), 'w') as f:
                    pass

            # Copy font files
            for f in self._fonts:
                src = os.path.join(self.ROOT_PATH, self.FONT_DIR, f)
                dst = os.path.join(path, self.FONT_DIR)
                if not os.path.lexists(dst): os.mkdir(dst)
                copy2(src, dst)

            # Copy utils path
            kwargs['ignore'] = ignore_patterns(*pattern1)
            src = os.path.join(self.ROOT_PATH, self.UTILS_DIR)
            copytree(src, path, **kwargs)
            # Copy platform file
            src = os.path.join(self.ROOT_PATH, self.PY_VER_DIR,
                               f'{platform}.py')
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

    def _fix_files(self, packages, platform):
        for src, path in packages.items():
            for pyfile, fix_imports, mcu in self.FIX_FILES:
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

                if fix_imports is not None:
                    fix_imports(self, process_path)

                if ((self._options.strip and platform in self.STRIP_PLATFORMS)
                    or self._options.force):
                    self._strip_doc_strings(process_path)
                    self._strip_comments(process_path)
                    self._strip_linefeeds(process_path)

                if platform in self.STRIP_PLATFORMS:
                    if os.path.isdir(process_path):
                        if process_path.endswith(self.FONT_DIR):
                            for f in self._fonts:
                                font_path = os.path.join(process_path, f)
                                self._cross_compile(font_path, platform)
                        else:
                            raise OSError(f"Unknown directory: {process_path}")
                    else:
                        self._cross_compile(process_path, platform)

    def _cross_compile(self, process_path, platform):
        arch_num = self._options.compress

        if arch_num != -1:
            if platform == self.STRIP_PLATFORMS[0]: # circuitpython
                mpy_cross = 'mpy-cross-cp'
            else: # micropython
                mpy_cross = 'mpy-cross'

            mpy_cross_path = os.path.join(
                os.getenv('VIRTUAL_ENV'), 'bin', mpy_cross)

            if arch_num > 0:
                arch_type = self.M_COMPRESS[arch_num+1][0]
                arch = f"-march={arch_type} -X emit=bytecode "
            else:
                arch = ""

            opt = f"-O{self._options.opt_level} "
            cmd = f"{mpy_cross_path} {opt}{arch}{process_path}"
            os.system(cmd)
            os.remove(process_path)

    def _strip_doc_strings(self, process_path):
        if self._options.debug: sys.stdout.write(
            f"_strip_doc_strings: {process_path}\n")

        if os.path.isdir(process_path): # Font files
            for f in self._fonts:
                with StringIO() as buff:
                    path = os.path.join(process_path, f)
                    self.__strip_doc_strings(buff, path)
                    self._write_file(buff, path)
        else:
            with StringIO() as buff:
                self.__strip_doc_strings(buff, process_path)
                self._write_file(buff, process_path)

    def __strip_doc_strings(self, buff, process_path):
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
        with open(process_path, 'r') as f:
            quote_flag = False
            code_flag = False

            for idx, line in enumerate(f, start=1):
                sre = self.RX_QUOTES.search(line)

                if sre:
                    lb, code, quote = sre.groups()
                    lb = '#' in lb
                    code = len(code) > 0
                    quote = '"""' == quote.replace("'''", '"""')
                    lb_code = '#' in sre.groups()[1]

                    if not lb and not lb_code:                     # 1 & 2
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

    def _strip_comments(self, process_path):
        if self._options.debug: sys.stdout.write(
            f"_strip_comments: {process_path}\n")

        if os.path.isdir(process_path): # Font files
            for f in self._fonts:
                with StringIO() as buff:
                    path = os.path.join(process_path, f)
                    self.__strip_comments(buff, path)
                    self._write_file(buff, path)
        else:
            with StringIO() as buff:
                self.__strip_comments(buff, process_path)
                self._write_file(buff, process_path)

    def __strip_comments(self, buff, process_path):
        with open(process_path, 'r') as f:
            quote_flag = False
            code_flag = False

            for idx, line in enumerate(f, start=1):
                sre = self.RX_QUOTES.search(line)

                if sre:
                    lb, code, quote = sre.groups()
                    lb = '#' in lb
                    code = len(code) > 0
                    lb_code = '#' in sre.groups()[1]
                    quote = '"""' == quote.replace("'''", '"""')

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
                sre = self.RX_1ST_HASH.search(line)

                if sre:
                    lb1st = sre.groups()[0]
                    lb1st = lb1st is not None and '#' in lb1st
                    if lb1st and not quote_flag and not code_flag: continue

                # Handle line where there is code followed by a #
                sre = self.RX_HASH_CODE.search(line)

                if sre:
                    lsdq, hlb, rsdq = sre.groups()
                    lsdq = (False if lsdq is None
                            else '"' == lsdq.replace("'", '"'))
                    hlb = '#' in hlb
                    rsdq = (False if rsdq is None
                            else '"' == rsdq.replace("'", '"'))

                    if hlb and (not lsdq or not rsdq):
                        line = line[:line.index('#')].rstrip() + '\n'

                buff.write(line)

    def _write_file(self, buff, process_path):
        if not self._options.noop:
            with open(process_path, 'w') as f:
                f.write(buff.getvalue().lstrip())

    def _strip_linefeeds(self, process_path):
        if self._options.debug: sys.stdout.write(
            f"_strip_linefeeds: {process_path}\n")

        if os.path.isdir(process_path): # Font files
            for f in self._fonts:
                with StringIO() as buff:
                    path = os.path.join(process_path, f)
                    self.__strip_linefeeds(buff, path)
                    self._write_file(buff, path)
        else:
            with StringIO() as buff:
                self.__strip_linefeeds(buff, process_path)
                self._write_file(buff, process_path)

    def __strip_linefeeds(self, buff, process_path):
        with open(process_path, 'r') as f:
            num_lf = 0

            for line in f:
                sre = self.RX_LF.search(line)

                if sre:
                    num_lf += 1

                    if num_lf > 1:
                        continue
                else:
                    num_lf = 0

                buff.write(line)


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
        dest='raspberrypi', help="Create a Raspberry Pi package."
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
        '-f', '--fonts', action='store_true', default=False, dest='fonts',
        help="Choose which fonts to put in the final packages."
        )
    parser.add_argument(
        '-s', '--strip', action='store_true', default=False,
        dest='strip', help=("Strip comments and non-code white space on "
                            "the MicroPython and CircuitPython packages.")
        )
    parser.add_argument(
        '-F', '--force-strip', action='store_true', default=False,
        dest='force', help=("Force striping on all packages including "
                            "the Raspberry Pi and Computer packages.")
        )
    parser.add_argument(
        '-L', '--list-compress', action='store_true', default=False,
        dest='compress_list', help=("List cross compile architecture types.")
        )
    parser.add_argument(
        '-C', '--compress', type=int, metavar='arch-type', default=-1,
        dest='compress', help=("Enter the number of the cross compile "
                               "architecture type.")
        )
    parser.add_argument(
        '-O', '--opt-level', type=int, metavar='opt-level', default=0,
        dest='opt_level', help=("Enter the optimization level for the "
                                "cross compiler.")
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
        options.raspberrypi = True

    if options.ili9225 or options.ili9341 or options.compress_list:
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
        sys.stdout.write("\nAt least one or both ILI9225 or ILI9341 "
                         "must be chosen.\n")

    sys.exit(exit_val)
