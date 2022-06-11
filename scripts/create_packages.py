#!/usr/bin/env python3
#
# scripts/create_packages.py
#
# This script creates the packages for all platforms.
#

import os
import sys
from shutil import copytree, ignore_patterns


class CreatePackages:
    """
    Creates packages.
    """
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    IMPORT_FIXES = ('ILI9225/ili9225.py',
                    'ILI9225/utils/compatibility.py',
                    'ILI9225/py_versions/circuitpython.py',
                    'ILI9225/py_versions/computer.py',
                    'ILI9225/py_versions/micropython.py',
                    'ILI9225/py_versions/raspberrypi.py')

    def __init__(self, options):
        self._options = options

    def start(self):
        build_path = os.path.join(self.ROOT_PATH, 'build')
        if not os.path.lexists(build_path): os.mkdir(build_path)
        packages = {}

        if self._options.ili9225:
            name = 'ILI9225'
            path_package = os.path.join(build_path, name)
            packages[name] = path_package
            if not os.path.lexists(path_package): os.mkdir(path_package)

        if self._options.ili9341:
            name = 'ILI9341'
            path_package = os.path.join(build_path, name)
            packages[name] = path_package
            if not os.path.lexists(path_package): os.mkdir(path_package)

        self._copy_code(packages)
        self._fix_imports()
        if self._options.circuitpython: self._create_circuitpython(build_path)
        if self._options.micropython: self._create_micropython(build_path)
        if self._options.raspi: self._create_raspi(build_path)

    def _copy_code(self, packages):
        pattern0 = ('__pycache__', 'tests')
        pattern1 = pattern0 + ('__init__.py',)

        for src, path in packages.items():
            copytree(src, path,
                     ignore=ignore_patterns(*pattern0),
                     dirs_exist_ok=True)
            src = 'utils'
            #dst = os.path.join(path, src)
            copytree(src, path,
                     ignore=ignore_patterns(*pattern1),
                     dirs_exist_ok=True)
            src = 'py_versions'
            #dst = os.path.join(path, src)
            copytree(src, path,
                     ignore=ignore_patterns(*pattern1),
                     dirs_exist_ok=True)
            src = 'fonts'
            dst = os.path.join(path, src)
            copytree(src, dst,
                     ignore=ignore_patterns(*pattern1),
                     dirs_exist_ok=True)

    def _fix_imports(self):
        pass


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
        '-n', '--noop', action='store_true', default=False, dest='noop',
        help="Run as if creating, but do nothing."
        )
    parser.add_argument(
        '-a', '--all', action='store_true', default=False,
        dest='all', help="Create all packages."
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
        dest='force', help=("Force striping all packages including the "
                            "Raspberry Pi package.")
        )
    parser.add_argument(
        '-D', '--debug', action='store_true', default=False, dest='debug',
        help="Run in debug mode."
        )
    options = parser.parse_args()
    exit_val = 0

    if options.debug:
        sys.stderr.write(f"DEBUG--options: {options}\n")

    if options.all:
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
