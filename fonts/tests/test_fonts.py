#
# fonts/tests/test_fonts.py
#

import os
import glob
import unittest
import importlib


class TestFonts(unittest.TestCase):
    """
    Test all font class.
    """

    def __init__(self, name):
        super().__init__(name)
        self._modules = self.import_fonts()

    def import_fonts(self):
        modules = {}

        for font in self.get_fonts():
            package = importlib.import_module(font)
            tmp, sep, name = font.rpartition('.')
            modules[name] = package

        return modules

    def get_fonts(self):
        for font in self.fonts():
            yield font

    def fonts(self):
        """
        Return a list of fonts as in fonts/<filename>.
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.dirname(this_dir)
        base_dir = os.path.dirname(font_dir)
        files = "{}/*.py".format(os.path.abspath(font_dir))
        font_files = [f.replace(base_dir + '/', ''
                                ).replace('/', '.').replace('.py', '')
                      for f in glob.glob(files)
                      if not f.endswith(('__init__.py', 'font_convert.py'))]
        return font_files

    def test_bitmap_in_fonts(self):
        """
        Test that the bitmap list exists in the fonts.

        .. notes::

            The bitmap variable has the following fields.
            [offset, width, height, advance cursor, x offset, y offset]
        """
        for name, module in self._modules.items():
            bitmap = getattr(module, "{name}Bitmap")
            self.assertFalse(True, msg="{name}: {len(bitmap)}")
