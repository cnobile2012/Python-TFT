#!/usr/bin/env python3
#
# scripts/create_packages.py
#
# This script creates the packages for all platforms.
#

import os
import sys
from io import StringIO
from shutil import copytree, ignore_patterns


class CreatePackages:
    """
    Creates packages.
    """
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    BUILD_PATH = 'build'
    ILI9225 = 'ILI9225'
    ILI9341 = 'ILI9341'

    def __init__(self, options):
        self._options = options

    def start(self):
        build_path = os.path.join(self.ROOT_PATH, self.BUILD_PATH)
        if not os.path.lexists(build_path): os.mkdir(build_path)
        packages = {}

        if self._options.ili9225:
            path_package = os.path.join(build_path, self.ILI9225)
            packages[self.ILI9225] = path_package
            if not os.path.lexists(path_package): os.mkdir(path_package)

        if self._options.ili9341:
            path_package = os.path.join(build_path, self.ILI9341)
            packages[self.ILI9341] = path_package
            if not os.path.lexists(path_package): os.mkdir(path_package)

        self._copy_code(packages)
        self._fix_files(packages)
        if self._options.circuitpython: self._create_circuitpython(build_path)
        if self._options.micropython: self._create_micropython(build_path)
        if self._options.raspi: self._create_raspi(build_path)

    def _copy_code(self, packages):
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
            src = 'py_versions'
            copytree(src, path, **kwargs)

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

    def _fix_ili9225(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_ili9225(self, process_path):
        pass

    def _fix_ili9341(self, process_path):
        pass

    def _strip_ili9341(self, process_path):
        pass

    def _fix_init(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_init(self, process_path):
        pass

    def _fix_compatibility(self, process_path):
        fix = "from py_versions."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_compatibility(self, process_path):
        pass

    def _strip_common(self, process_path):
        pass

    def _fix_circuitpython(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_circuitpython(self, process_path):
        pass

    def _fix_computer(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_computer(self, process_path):
        pass

    def _strip_default_fonts(self, process_path):
        pass

    def _fix_micropython(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_micropython(self, process_path):
        pass

    def _fix_raspberrypi(self, process_path):
        fix = "from utils."
        change = "from ."
        self.__fix_imports(process_path, fix, change)

    def _strip_raspberrypi(self, process_path):
        pass

    FIX_FILES = (
        ('{}/{}/ili9225.py', _fix_ili9225, _strip_ili9225),
        ('{}/{}/ili9341.py', _fix_ili9341, _strip_ili9341),
        ('{}/{}/__init__.py', _fix_init, _strip_init),
        ('{}/{}/compatibility.py', _fix_compatibility, _strip_compatibility),
        ('{}/{}/common.py', None, _strip_common),
        ('{}/{}/circuitpython.py', _fix_circuitpython, _strip_circuitpython),
        ('{}/{}/computer.py', _fix_computer, _strip_computer),
        ('{}/{}/default_fonts.py', None, _strip_default_fonts),
        ('{}/{}/micropython.py', _fix_micropython, _strip_micropython),
        ('{}/{}/raspberrypi.py', _fix_raspberrypi, _strip_raspberrypi),
        )

    def _fix_files(self, packages):
        for src, path in packages.items():
            for pyfile, fix, strip in self.FIX_FILES:
                if self.ILI9225 == src:
                    process_path = pyfile.format(self.BUILD_PATH, self.ILI9225)
                elif self.ILI9341 == src:
                    process_path = pyfile.format(self.BUILD_PATH, self.ILI9341)

                if fix is not None: fix(self, process_path)
                if self._options.strip: strip(self, process_path)

    def _create_circuitpython(self, path):
        c_path = os.path.join(path, 'circuitpython')
        if not os.path.lexists(c_path): os.mkdir(c_path)


    def _create_micropython(self, path):
        m_path = os.path.join(path, 'micropython')
        if not os.path.lexists(m_path): os.mkdir(m_path)


    def _create_raspi(self, path):
        r_path = os.path.join(path, 'raspi')
        if not os.path.lexists(r_path): os.mkdir(r_path)







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
        '-p', '--computer', action='store_true', default=False,
        dest='computer', help="Create a Computer package."
        )
    parser.add_argument(
        '-c', '--circuitpython', action='store_true', default=False,
        dest='circuitpython', help="Create a CircuitPython package."
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
        dest='strip', help="Strip comments and non-code white space."
        )
    parser.add_argument(
        '-f', '--force-strip', action='store_true', default=False,
        dest='force', help=("Force striping on all packages including "
                            "the Raspberry Pi and Computer packages.")
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
