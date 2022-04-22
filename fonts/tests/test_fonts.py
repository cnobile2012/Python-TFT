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
    BITMAP_MASK = "{}Bitmaps"
    GLYPHS_MASK = "{}Glyphs"

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

    def test_bitmap_var_in_fonts(self):
        """
        Test that the bitmaps list exists in the fonts and is not
        zero length.
        """
        for name, module in self._modules.items():
            bitmaps = []
            var_name = self.BITMAP_MASK.format(name)

            try:
                tmp = getattr(module, var_name)
            except AttributeError as e:
                msg - f"Font '{name}' does not have a '{var_name}' variable."
                self.assertTrue(bitmaps, msg=msg)
            else:
                if isinstance(tmp, list):
                    bitmaps[:] = tmp
                    msg = (f"Font '{name}', '{var_name}' variable is "
                           "zero length.")
                    self.assertNotEqual(len(bitmaps), 0, msg=msg)

    def test_glyphs_var_in_fonts(self):
        """
        Test that the glyphs list exists in the fonts and it is not
        zero length. Also test that the length of each glyph is correct.

        .. notes::

            The glyphs variable has the following fields.
            [offset, width, height, advance cursor, x offset, y offset]
        """
        for name, module in self._modules.items():
            glyphs = []
            glyph_size = 6
            var_name = self.GLYPHS_MASK.format(name)

            try:
                tmp = getattr(module, var_name)
            except AttributeError as e:
                msg - f"Font '{name}' does not have a '{var_name}' variable"
                self.assertTrue(bitmaps, msg=msg)
            else:
                if isinstance(tmp, list):
                    glyphs[:] = tmp
                    tmp_msg = (f"Font '{name}': should be {glyph_size} in "
                               "length found: {{}}")

                    for lst in glyphs:
                        found_size = len(lst)
                        msg = tmp_msg.format(found_size)
                        self.assertEqual(glyph_size, found_size, msg=msg)

    def test_font_var_in_fonts(self):
        """
        Test that the font list exists in the fonts and it is not
        zero length.

        .. notes::

            The font variable is a combination of the other two variables
            plus three other values. The following fields should exist.
            [bitmap var, glyph var, first extent, last extent, y advance]
        """
        for name, module in self._modules.items():
            font = []
            font_size = 5

            try:
                tmp = getattr(module, name)
            except AttributeError as e:
                msg - f"Font '{name}' does not have a '{name}' variable"
                self.assertTrue(bitmaps, msg=msg)
            else:
                if isinstance(tmp, list):
                    font[:] = tmp
                    found_size = len(font)
                    msg = (f"Font '{name}': should be {font_size} in "
                           f"length found: {found_size}")
                    self.assertEqual(font_size, found_size, msg=msg)
                    tmp_msg = "{} item should be a {}, found {}"

                    for idx, item in enumerate(font, start=1):
                        if idx < 3:
                            num = f"{idx}{'st' if idx == 1 else 'nd'}"
                            msg = tmp_msg.format(num, 'list', idx)
                            self.assertTrue(isinstance(item, list), msg=msg)
                        else:
                            num = f"{idx}{'rd' if idx == 3 else 'th'}"
                            msg = tmp_msg.format(num, 'int', idx)
                            self.assertTrue(isinstance(item, int), msg=msg)

    @unittest.skip("This test does not work because the variable cannot "
                   "be set dynamically.")
    def test_extended_var_in_fonts(self):
        """
        Every so often a font has an extended range as in the TomThumb font.
        This needs to be tested also.
        """
        for name, module in self._modules.items():
            list_names = (self.BITMAP_MASK.format(name),
                          self.GLYPHS_MASK.format(name),
                          name)

            for any_name in [n for n in dir(module) if not n.startswith("_")]:
                if any_name not in list_names:
                    # We don't need to test the last variable in list_names.
                    for var_name in list_names[:-1]:
                        font_list = []

                        try:
                            font_list[:] = getattr(module, var_name)
                        except AttributeError as e:
                            msg - (f"Font '{name}' does not have a "
                                   "'{var_name}' variable")
                            self.assertTrue(bitmaps, msg=msg)
                        else:
                            size_before = len(font_list)
                            # THIS LINE DOES'T WORK.
                            setattr(module, name, 1)
                            font_list[:] = getattr(module, var_name)
                            size_after  = len(font_list)
                            msg = (f"Font '{name}': variable '{var_name}', "
                                   f"unextended size '{size_before}', should "
                                   "be less than the extended size of "
                                   f"'{size_after}'")
                            self.assertTrue(size_before < size_after, msg=msg)
