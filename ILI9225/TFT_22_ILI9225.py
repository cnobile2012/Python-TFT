# -*- coding: utf-8 -*-
"""
TFT_22_ILI9225.py

Driver for the ILI9225 chip TFT LCD displays.
"""

from utils.compatibility import Compatibility, Boards, CompatibilityException
from utils.common import RGB16BitColor


class TFTException(Exception):
    pass


class AutoIncMode:
    R2L_BOTTOM_UP = 0
    BOTTOM_UP_R2L = 1
    L2R_BOTTOM_UP = 2
    BOTTOM_UP_L2R = 3
    R2L_TOP_DOWN = 4
    TOP_DOWN_R2L = 5
    L2R_TOP_DOWN = 6
    TOP_DOWN_L2R = 7


class CurrentFont:
    """
    Stores the currently used font.
    """

    def __init__(self, args=((), 0, 0, 0, 0, 0, False)):
        self.set_font(args)

    def set_font(self, args):
        self.font = args[0]
        self.width = args[1]
        self.height = args[2]
        self.offset = args[3]
        self.numchars = args[4]
        self.nbrows = int(args[5])
        self.mono_sp = args[6]


class GFXGlyph:
    """
    Glyph structure data.
    """

    def __init__(self, glyph):
        self.bitmap_offset = glyph[0] # GFXFont.bitmap
        self.width = glyph[1]         # Bitmap dimensions in pixels
        self.height = glyph[2]
        self.x_advance = glyph[3]     # Distance to advance cursor (x axis)
        self.x_offset = glyph[4]      # Distance from cursor pos to UL corner
        self.y_offset = glyph[5]


class GFXFont:
    """
    Font meta data.
    """

    def __init__(self, font):
        self.bitmap = font[0]    # Glyph bitmaps, concatenated
        self.glyph = font[1]     # Glyph class
        self.first = font[3]     # ASCII extents
        self.last = font[4]
        self.y_advance = font[5] # Newline distance (y axis)


class ILI9225(Compatibility):
    """
    Main ILI9225 class.
    """
    LCD_WIDTH = 176
    LCD_HEIGHT = 220
    INVOFF                  = 0x20  # Invert off
    INVON                   = 0x21  # Invert on

    DRIVER_OUTPUT_CTRL      = 0x01  # Driver Output Control
    LCD_AC_DRIVING_CTRL     = 0x02  # LCD AC Driving Control
    ENTRY_MODE              = 0x03  # Entry Mode
    DISP_CTRL1              = 0x07  # Display Control 1
    BLANK_PERIOD_CTRL1      = 0x08  # Blank Period Control
    FRAME_CYCLE_CTRL        = 0x0B  # Frame Cycle Control
    INTERFACE_CTRL          = 0x0C  # Interface Control
    OSC_CTRL                = 0x0F  # Osc Control
    POWER_CTRL1             = 0x10  # Power Control 1
    POWER_CTRL2             = 0x11  # Power Control 2
    POWER_CTRL3             = 0x12  # Power Control 3
    POWER_CTRL4             = 0x13  # Power Control 4
    POWER_CTRL5             = 0x14  # Power Control 5
    VCI_RECYCLING           = 0x15  # VCI Recycling
    RAM_ADDR_SET1           = 0x20  # Horizontal GRAM Address Set
    RAM_ADDR_SET2           = 0x21  # Vertical GRAM Address Set
    GRAM_DATA_REG           = 0x22  # GRAM Data Register
    GATE_SCAN_CTRL          = 0x30  # Gate Scan Control Register
    VERTICAL_SCROLL_CTRL1   = 0x31  # Vertical Scroll Control 1 Register
    VERTICAL_SCROLL_CTRL2   = 0x32  # Vertical Scroll Control 2 Register
    VERTICAL_SCROLL_CTRL3   = 0x33  # Vertical Scroll Control 3 Register
    PARTIAL_DRIVING_POS1    = 0x34  # Partial Driving Position 1 Register
    PARTIAL_DRIVING_POS2    = 0x35  # Partial Driving Position 2 Register
    HORIZONTAL_WINDOW_ADDR1 = 0x36  # Horizontal Address Start Position
    HORIZONTAL_WINDOW_ADDR2 = 0x37  # Horizontal Address End Position
    VERTICAL_WINDOW_ADDR1   = 0x38  # Vertical Address Start Position
    VERTICAL_WINDOW_ADDR2   = 0x39  # Vertical Address End Position
    GAMMA_CTRL1             = 0x50  # Gamma Control 1
    GAMMA_CTRL2             = 0x51  # Gamma Control 2
    GAMMA_CTRL3             = 0x52  # Gamma Control 3
    GAMMA_CTRL4             = 0x53  # Gamma Control 4
    GAMMA_CTRL5             = 0x54  # Gamma Control 5
    GAMMA_CTRL6             = 0x55  # Gamma Control 6
    GAMMA_CTRL7             = 0x56  # Gamma Control 7
    GAMMA_CTRL8             = 0x57  # Gamma Control 8
    GAMMA_CTRL9             = 0x58  # Gamma Control 9
    GAMMA_CTRL10            = 0x59  # Gamma Control 10

    # 1: pixel width of 1 font character, 2: pixel height
    _CFONT_HEADER_SIZE = 4

    # Corresponding modes when orientation changes.
    _MODE_TAB = (
        (AutoIncMode.BOTTOM_UP_L2R, AutoIncMode.L2R_BOTTOM_UP,
         AutoIncMode.TOP_DOWN_L2R, AutoIncMode.L2R_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_R2L, AutoIncMode.R2L_BOTTOM_UP,
         AutoIncMode.TOP_DOWN_R2L, AutoIncMode.R2L_TOP_DOWN), # 90°
        (AutoIncMode.L2R_TOP_DOWN, AutoIncMode.TOP_DOWN_L2R,
         AutoIncMode.R2L_TOP_DOWN, AutoIncMode.TOP_DOWN_R2L,
         AutoIncMode.L2R_BOTTOM_UP, AutoIncMode.BOTTOM_UP_L2R,
         AutoIncMode.R2L_BOTTOM_UP, AutoIncMode.BOTTOM_UP_R2L), # 180°
        (AutoIncMode.TOP_DOWN_R2L, AutoIncMode.R2L_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_R2L, AutoIncMode.R2L_BOTTOM_UP,
         AutoIncMode.TOP_DOWN_L2R, AutoIncMode.L2R_TOP_DOWN,
         AutoIncMode.BOTTOM_UP_L2R, AutoIncMode.L2R_BOTTOM_UP) # 270°
        )

    def __init__(self, rst, rs, cs, *, led=-1, sdi=-1, clk=-1, brightness=255,
                 board=None, mode=None):
        """
        Initialize the ILI9225 class.

        .. note::

          1. Constructor when using software SPI. All output pins are
             configurable (_hw_spi=False).
          2. Constructor when using software SPI. All output pins are
             configurable (_hw_spi=False). Adds backlight brightness 0-255
          3. Constructor when using hardware SPI. Faster, but must use SPI
             pins specific to each board type (_hw_spi=True).
          4. Constructor when using hardware SPI. Faster, but must use SPI
             pins specific to each board type (_hw_spi=True). Adds backlight
             brightness 0-255

        @param rst: The RST (reset) pin on the display. (RTD on some devices.)
        @type rst: int
        @param rs: The RS (command/data) pin on the display. 0: command, 1: data
        @type rs: int
        @param cs: The CS (chip select) pin on the display.
        @type cs: int
        @param led: The LED pin on the display.
        @type led: int
        @param sdi: The SDI (serial data input) pin on the display. Sometimes
                    marked the SDA pin.
        @type sdi: int
        @param clk: The CLK (clock) pin on the display.
        @type clk: int
        @param brightness: Set the brightness from 0..255 (default=255).
        @type brightness: int
        @param board: The board this will run on. e.g. Boards.ESP32
        @type board: int
        @param mode: Only applies to the Raspberry Pi and Computer boards.
                     Default GPIO.BCM
        @type mode: int
        """
        super().__init__(mode=mode)
        self._rst = rst
        self._rs = rs
        self._cs = cs
        self._led = led
        self._sdi = sdi
        self._clk = clk
        self._brightness = brightness # Set to maximum brightness.
        self._orientation = 0
        self._hw_spi = True if sdi == -1 and clk == -1 else False
        self._bl_state = True
        self._max_x = 0
        self._max_y = 0
        self._bg_color = RGB16BitColor.COLOR_BLACK
        self._write_function_level = 0
        self._current_font = None
        self._cfont = CurrentFont()
        self._gfx_font = None

        if board is not None:
            try:
                self.set_board(board)
            except CompatibilityException as e:
                print(e)
        else:
            print("Warning: The board has not been set. The board "
                  "keyword argument must be passed during instantiation or "
                  "the set_board() method must be run after instantiation.")

    def begin(self):
        # Setup reset pin.
        self.pin_mode(self._rst, self.OUTPUT)
        self.digital_write(self._rst, self.LOW)

        # Set up backlight pin, turn off initially.
        if self._led >= 0:
            self.pin_mode(self._led, self.OUTPUT)
            self.set_backlight(False)

        # Control pins
        self.pin_mode(self._rs, self.OUTPUT);
        self.digital_write(self._rs, self.LOW);
        self.pin_mode(self._cs, self.OUTPUT);
        self.digital_write(self._cs, self.HIGH)

        # Software SPI
        if self._clk >= 0 and self._sdi >= 0:
            self.pin_mode(self._sdi, self.OUTPUT)
            self.digital_write(self._sdi, self.LOW);
            self.pin_mode(self._clk, self.OUTPUT)
            self.digital_write(self._clk, self.HIGH);

        # Pull the reset pin high to release the ILI9225C from the reset
        # status.
        self.digital_write(self._rst, self.HIGH)
        self.delay(1)
        # Pull the reset pin low to reset the ILI9225.
        self.digital_write(self._rst, self.LOW)
        self.delay(10)
        # Pull the reset pin high to release the ILI9225C from the reset
        # status.
        self.digital_write(self._rst, self.HIGH)
        self.delay(50)

        # Start initial sequence.
        # Set SS bit and direction output from S528 to S1
        self.__start_write()
        # Set SAP,DSTB,STB
        self._write_register(self.POWER_CTRL1, 0x0000)
        # Set APON,PON,AON,VCI1EN,VC
        self._write_register(self.POWER_CTRL2, 0x0000)
        # Set BT,DC1,DC2,DC3
        self._write_register(self.POWER_CTRL3, 0x0000)
        # Set GVDD
        self._write_register(self.POWER_CTRL4, 0x0000)
        # Set VCOMH/VCOML voltage
        self._write_register(self.POWER_CTRL4, 0x0000)
        self.__end_write()
        self.delay(40)

        # Power-on sequence
        self.__start_write()
        # Set APON,PON,AON,VCI1EN,VC
        self._write_register(self.POWER_CTRL2, 0x0018)
        # Set BT,DC1,DC2,DC3
        self._write_register(self.POWER_CTRL3, 0x6121)
        # Set GVDD (007F 0088)
        self._write_register(self.POWER_CTRL4, 0x006F)
        # Set VCOMH/VCOML voltage
        self._write_register(self.POWER_CTRL4, 0x495F)
        # Set SAP,DSTB,STB
        self._write_register(self.POWER_CTRL1, 0x0800)
        self.__end_write()
        self.delay(10)
        self.__start_write()
        # Set APON,PON,AON,VCI1EN,VC
        self._write_register(self.POWER_CTRL2, 0x103B)
        self.__end_write()
        self.delay(50)

        self.__start_write()
        # Set the display line number and display direction
        self._write_register(self.DRIVER_OUTPUT_CTRL, 0x011C)
        # Set 1 line inversion
        self._write_register(self.LCD_AC_DRIVING_CTRL, 0x0100)
        # Set GRAM write direction and BGR=1.
        self._write_register(self.ENTRY_MODE, 0x1038)
        # Display off
        self._write_register(self.DISP_CTRL1, 0x0000)
        # Set the back porch and front porch
        self._write_register(self.BLANK_PERIOD_CTRL1, 0x0808)
        # Set the clocks number per line
        self._write_register(self.FRAME_CYCLE_CTRL, 0x1100)
        # CPU interface
        self._write_register(self.INTERFACE_CTRL, 0x0000)
        # 0e01
        self._write_register(self.OSC_CTRL, 0x0D01)
        # Set VCI recycling
        self._write_register(self.VCI_RECYCLING, 0x0020)
        # RAM Address
        self._write_register(self.RAM_ADDR_SET1, 0x0000)
        self._write_register(self.RAM_ADDR_SET2, 0x0000)

        # Set GRAM area
        self._write_register(self.GATE_SCAN_CTRL, 0x0000)
        self._write_register(self.VERTICAL_SCROLL_CTRL1, 0x00DB)
        self._write_register(self.VERTICAL_SCROLL_CTRL2, 0x0000)
        self._write_register(self.VERTICAL_SCROLL_CTRL3, 0x0000)
        self._write_register(self.PARTIAL_DRIVING_POS1, 0x00DB)
        self._write_register(self.PARTIAL_DRIVING_POS2, 0x0000)
        self._write_register(self.HORIZONTAL_WINDOW_ADDR1, 0x00AF)
        self._write_register(self.HORIZONTAL_WINDOW_ADDR2, 0x0000)
        self._write_register(self.VERTICAL_WINDOW_ADDR1, 0x00DB)
        self._write_register(self.VERTICAL_WINDOW_ADDR2, 0x0000)

        # Set GAMMA curve
        self._write_register(self.GAMMA_CTRL1, 0x0000)
        self._write_register(self.GAMMA_CTRL2, 0x0808)
        self._write_register(self.GAMMA_CTRL3, 0x080A)
        self._write_register(self.GAMMA_CTRL4, 0x000A)
        self._write_register(self.GAMMA_CTRL5, 0x0A08)
        self._write_register(self.GAMMA_CTRL6, 0x0808)
        self._write_register(self.GAMMA_CTRL7, 0x0000)
        self._write_register(self.GAMMA_CTRL8, 0x0A00)
        self._write_register(self.GAMMA_CTRL9, 0x0710)
        self._write_register(self.GAMMA_CTRL10, 0x0710)

        self._write_register(self.DISP_CTRL1, 0x0012)
        self.__end_write()
        self.delay(50)
        self.__start_write()
        self._write_register(self.DISP_CTRL1, 0x1017)
        self.__end_write()

        # Turn on backlight
        self.set_backlight(True)
        self.set_orientation(0)

        # Initialize variables
        self.set_background_color(RGB16BitColor.COLOR_BLACK)
        self.clear()

    def clear(self):
        old_orientation = self._orientation
        self.set_orientation(0)
        self.fill_rectangle(0, 0, self._max_x - 1, self._max_y - 1,
                            self.COLOR_BLACK)
        self.set_orientation(old_orientation)
        self.delay(10)

    def invert(self, flag):
        """
        Invert the screen.

        @param flag: True = invert and False = normal screen.
        @type flag: bool
        """
        self.__start_write()
        self.spi_write(self.INVON if flag else self.INVOFF)
        self.__end_write()

    def set_backlight(self, flag):
        """
        Set the backlight on or off.

        @param flag: True = backlight on and False = backlight off.
        @type flag: bool
        """
        self._bl_state = flag
        # #ifndef ESP32
        #     if (_led) analogWrite(_led, blState ? _brightness : 0);
        # #endif

    def set_backlight_brightness(self, brightness):
        """
        Set the backlight brightness.

        @param brightness: Set the brightness to 0..255
        @type brightness: int
        """
        self._brightness = brightness
        self.set_backlight(self._bl_state)

    def set_display(self, flag):
        """
        Set the display on or off.

        @param flag: True = display on and False = display off.
        @type flag: bool
        """
        if flag:
            self.__start_write()
            self._write_register(0x00ff, 0x0000)
            self._write_register(POWER_CTRL1, 0x0000)
            self.__end_write()
            self.delay(50)
            self.__start_write()
            self._write_register(DISP_CTRL1, 0x1017)
            self.__end_write()
            self.delay(200)
        else:
            self.__start_write()
            self._write_register(0x00ff, 0x0000)
            self._write_register(DISP_CTRL1, 0x0000)
            self.__end_write()
            self.delay(50)
            self.__start_write()
            self._write_register(POWER_CTRL1, 0x0003)
            self.__end_write()
            self.delay(200)

    def set_background_color(self, color=RGB16BitColor.COLOR_BLACK):
        """
        Set the background color.

        @param color: Background color (default=black).
        @type color: int
        """
        self._bg_color = color

    def set_orientation(self, orientation):
        """
        Set the orientation.

        @param orientation: 0=portrait, 1=right rotated landscape,
                            2=reverse portrait, 3=left rotated landscape
        @type orientation: int
        """
        self._orientation = orientation % 4

        if self._orientation == 0:
            self._max_x = LCD_WIDTH
            self._max_y = LCD_HEIGHT
        elif self._orientation == 1:
            self._max_x = LCD_HEIGHT
            self._max_y = LCD_WIDTH
        elif self._orientation == 2:
            self._max_x = LCD_WIDTH
            self._max_y = LCD_HEIGHT
        elif self._orientation == 3:
            self._max_x = LCD_HEIGHT
            self._max_y = LCD_WIDTH

    def get_orientation(self):
        """
        Get the orientation.

        @rtype Return the current orientation.
        """
        return self._orientation

    def get_screen_max_x(self):
        """
        ORIGINAL NAME maxX()

        Get the screen max x size.

        .. note::

          240 decimal means 240 pixels and thus 0..239 coordinates.

        @rtype Horizontal size of the screen in pixels.
        """
        return self._max_x

    def get_screen_max_y(self):
        """
        ORIGINAL NAME maxY()

        Get the screen max y size.

        .. note::

          240 decimal means 240 pixels and thus 0..239 coordinates.

        @rtype Vertical size of the screen in pixels.
        """
        return self._max_y

    #
    # Beginning of standard font methods.
    #
    def set_font(self, font, mono_sp=False):
        """
        Set the current font.

        @param font: The name of the font.
        @type font: str
        @param mono_sp: True = Mono spaced, False = Proportional
        @type mono_sp: bool
        """
        #       font, width,   height,  offset,  numchars, height / 8
        args = (font, font[0], font[1], font[2], font[3], font[1] / 8,
                mono_sp)
        self._cfont.set_font(args)

    def get_font(self):
        """
        Get the current font.

        @rtype Return the current font.
        """
        return self._cfont

    ## def get_font_x(self):
    ##     """
    ##     NEVER IMPLIMENTED IN C++ VERSION (fontX(void))
    ##     Get horizontal size of font.

    ##     @rtype Horizontal size of current font in pixels.
    ##     """
    ##     pass

    ## def get_font_y(self):
    ##     """
    ##     NEVER IMPLIMENTED IN C++ VERSION (fontY(void))
    ##     Get vertical size of font.

    ##     @rtype Vertical size of current font in pixels.
    ##     """
    ##     pass

    def draw_char(self, x, y, ch, color=RGB16BitColor.COLOR_WHITE):
        """
        Draw a character.

        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param ch: The character to draw on the display.
        @type ch: str
        @param color: A 16-bit color (default=white).
        @type color: int
        @rtype Width of character in display pixels.
        """
        self._is_font_set()
        char_offset = self.__get_offset(ch)

        # Monospaced: Get char width from font.
        if self._cfont.mono_sp:
            char_width = self._cfont.width
        else:
            char_width = self._read_font_byte(char_offset)

        char_offset += 1
        # Use autoincrement/decrement feature, if character fits
        # completely on screen.
        fast_mode = ((x - char_width + 1) < self._max_x
                     and (y + self._cfont.height - 1) < self._max_y)

        self.__start_write()

        # Set character window.
        if fast_mode:
            self._set_window(x, y, x + char_width + 1,
                             y + self._cfont.height + 1)

        # Each font "column" (+1 blank column for spacing).
        for i in range(char_width + 1):
            h = 0  # Keep track of char height.

            for j in range(self._cfont.nbrows): # Each column byte.
                if i == char_width:
                    charData = 0x0  # Insert blank column
                else:
                    char_data = self._read_font_byte(char_offset)

                char_offset += 1

                for k in range(8): # Process every row in font character.
                    if h >= self._cfont.height: break

                    if fast_mode:
                        self.spi_write(color if self._bit_read(
                            char_data, k) else self._bg_color)
                    else:
                        self.drawPixel(
                            x + i, y + (j * 8) + k, color
                            if self._bit_read(char_data, k)
                            else self._bg_color)

                    h += 1

        self.__end_write()
        self._reset_window()
        return char_width

    def get_char_width(self, ch):
        """
        Width of an ASCII character (pixel).

        @param ch: The ASCII character.
        @type ch: str
        @rtype Character width.
        """
        self._is_font_set()
        char_offset = self.__get_offset(ch)
        return self._read_font_byte(char_offset) # Get font width from 1st byte.

    def __get_offset(self, ch):
        # Bytes used by each character.
        char_offset = (self._cfont.width * self._cfont.nbrows) + 1
        # char offset (add 4 for font header)
        return (char_offset * (ch - self._cfont.offset)
                ) + self._CFONT_HEADER_SIZE

    def _is_font_set(self):
        if len(self._cfont.font) <= 0:
            raise TFTException("Please set a standard font before using "
                               "this method.")

    def _read_font_byte(self, index):
        return self._cfont.font[index]

    def _bit_read(self, value, bit):
        """
        Is bit out-of-range for value.

        @param value: The integer value.
        @type value: int
        @param bit: The bit within the value.
        @type bit: int
        @rtype Return a 1 if the bit is within the value range and 0 if
               out-of-range.
        """
        return ((value) >> (bit)) & 0x01
    #
    # End of standard font methods.
    #
    # Beginning of GFX font methods.
    #

    def set_gfx_font(self, font=None):
        """
        Set the GFX font.

        @param font: GFX font name defined in include file.
        @type font: str
        """
        self._gfx_font = GFXFont(font)

    def draw_gfx_text(self, x, y, s, color=RGB16BitColor.COLOR_WHITE):
        """
        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param s: The string to draw on the display.
        @type s: str
        @param color: A 16-bit color (default=white).
        @type color: int
        """
        currx = x

        if self._gfx_font:
            # Draw every character in the string.
            for ch in s:
                currx += self.draw_gfx_char(currx, y, ch, color) + 1

    def get_gfx_text_extent(self, x, y, s):
        """
        Get the width & height of a text string with the current GFX font

        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param s: The string to draw on the display.
        @type s: str
        @param w: Character width.
        @type w: int
        @param h: Character height.
        @type h: int
        @rtype A tuple of the width and height (width, height).
        """
        h = 0

        for ch in range(s):
            gw, gh, xa = self.get_gfx_char_extent(ch)
            if gh > h: h = gh
            w += xa

        return w, h

    def draw_gfx_char(self, x, y, ch, color=RGB16BitColor.COLOR_WHITE):
        """
        Draw a single character with the current GFX font.

        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param ch: Character to draw on the display.
        @type ch: int
        @param color: A 16-bit color (default=white).
        @type color: int
        """
        ch -= self._gfx_font.first
        glyph = GFXGlyph(self._gfx_font.glyph[ch])
        bitmap = self._gfx_font.bitmap
        bo = glyph.bitmap_offset
        w = glyph.width
        h = glyph.height
        xa = glyph.x_advance
        xo = glyph.x_offset
        yo = glyph.y_offset
        bits = bit = 0

        # Add character clipping here one day.
        self.__start_write()

        for yy in range(h):
            for xx in range(w):
                bit += 1

                if not (bit & 7):
                    bo += 1
                    bits = bitmap[bo]

                if bits & 0x80:
                    self.draw_pixel(x + xo + xx, y + yo + yy, color)

                bits <<= 1

        self.__end_write()
        return xa

    def get_gfx_char_extent(self, x, y, ch, color):
        """
        Draw a single character with the current GFX font.

        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param ch: The character to draw on the display.
        @type ch: str
        @param color: A 16-bit color.
        @type color: int
        """
        # Is char present in this font?
        if self._gfx_font.first <= ch >= self._gfx_font.last:
            glyph = GFXGlyph(self._gfx_font.glyph[ch])
            gw = glyph.width
            gh = glyph.height
            xa = glyph.x_advance

        return gw, gh, xa
    #
    # End of GFX font methods.
    #

    def draw_rectangle(self, x0, y0, x1, y1, color):
        """
        Draw a rectangle using rectangular coordinates.

        @param x0: Start point coordinate (x0-axis).
        @type x0: int
        @param y0: Center point coordinate (y0-axis).
        @type y0: int
        @param x1: Center point coordinate (x1-axis).
        @type x1: int
        @param y1: Center point coordinate (y1-axis).
        @type y1: int
        @param color: A 16-bit color.
        @type color: int
        """
        self.__start_write()
        self._draw_line(x0, y0, x0, y1, color)
        self._draw_line(x0, y0, x1, y0, color)
        self._draw_line(x0, y1, x1, y1, color)
        self._draw_line(x1, y0, x1, y1, color)
        self.__end_write()

    def fill_rectangle(self, x0, y0, x1, y1, color):
        """
        Fill a rectangle using rectangular coordinates.

        @param x0: Start point coordinate (x0-axis).
        @type x0: int
        @param y0: Center point coordinate (y0-axis).
        @type y0: int
        @param x1: Center point coordinate (x1-axis).
        @type x1: int
        @param y1: Center point coordinate (y1-axis).
        @type y1: int
        @param color: A 16-bit color
        @type color: int
        """
        self._set_window(x0, y0, x1, y1)
        self.__start_write()

        for t in range((y1 - y0 + 1) * (x1 - x0 + 1)):
            self.spi_write(color)

        self.__end_write()
        self._reset_window()

    def draw_circle(self, x0, y0, radius, color):
        """
        Draw a circle.

        @param x0: Center point coordinate (x-axis).
        @type x0: int
        @param y0: Center point coordinate (y-axis).
        @type y0: int
        @param radius: The radius of the circle.
        @type radius: int
        @param color: A 16-bit color.
        @type color: int
        """
        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x = 0
        y = radius

        self.__start_write()
        self.draw_pixel(x0, y0 + radius, color)
        self.draw_pixel(x0, y0 - radius, color)
        self.draw_pixel(x0 + radius, y0, color)
        self.draw_pixel(x0 - radius, y0, color)

        while x < y:
            if f >= 0:
                y += 1
                ddf_y += 2
                f += ddf_y

            x += 1
            ddf_x += 2
            f += ddf_x

            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
            self.draw_pixel(x0 + y, y0 + x, color)
            self.draw_pixel(x0 - y, y0 + x, color)
            self.draw_pixel(x0 + y, y0 - x, color)
            self.draw_pixel(x0 - y, y0 - x, color)

        self.__end_write()

    def fill_circle(self, x0, y0, radius, color):
        """
        Fill a circle.

        @param x0: Center point coordinate (x-axis).
        @type x0: int
        @param y0: Center point coordinate (y-axis).
        @type y0: int
        @param radius: The radius of the circle.
        @type radius: int
        @param color: A 16-bit color.
        @type color: int
        """
        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x = 0
        y = radius

        self.__start_write()

        while x < y:
            if f >= 0:
                y += 1
                ddf_y += 2
                f += ddf_y

            x += 1
            ddf_x += 2
            f += ddf_x

            self._draw_line(x0 + x, y0 + y, x0 - x, y0 + y, color) # bottom
            self._draw_line(x0 + x, y0 - y, x0 - x, y0 - y, color) # top
            self._draw_line(x0 + y, y0 - x, x0 + y, y0 + x, color) # right
            self._draw_line(x0 - y, y0 - x, x0 - y, y0 + x, color) # left

        self.__end_write()
        self.fill_rectangle(x0 - x, y0 - y, x0 + x, y0 + y, color)

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color):
        """
        Draw a triangle using triangular coordinates.

        @param x0: Start point coordinate (x0-axis).
        @type x0: int
        @param y0: Center point coordinate (y0-axis).
        @type y0: int
        @param x1: Center point coordinate (x1-axis).
        @type x1: int
        @param y1: Center point coordinate (y1-axis).
        @type y1: int
        @param x2: Center point coordinate (x1-axis).
        @type x2: int
        @param y2: Center point coordinate (y1-axis).
        @type y2: int
        @param color: A 16-bit color.
        @type color: int
        """
        self.__start_write()
        self._draw_line(x0, y0, x1, y1, color)
        self._draw_line(x1, y1, x2, y2, color)
        self._draw_line(x2, y2, x0, y0, color)
        self.__end_write()

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        """
        Fill solid triangle using triangular coordinates.

        @param x0: Start point coordinate (x0-axis).
        @type x0: int
        @param y0: Center point coordinate (y0-axis).
        @type y0: int
        @param x1: Center point coordinate (x1-axis).
        @type x1: int
        @param y1: Center point coordinate (y1-axis).
        @type y1: int
        @param x2: Center point coordinate (x1-axis).
        @type x2: int
        @param y2: Center point coordinate (y1-axis).
        @type y2: int
        @param color: A 16-bit color.
        @type color: int
        """
        # Sort coordinates by Y order (y2 >= y1 >= y0)
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        if y1 > y2:
            y2, y1 = y1, y2
            x2, x1 = x1, x2

        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        self.__start_write()

        # Handle awkward all-on-same-line case as its own thing.
        if y0 == y2:
            a = b = x0

            if x1 < a: a = x1
            elif x2 > b: b = x1

            if x2 < a: a = x2
            elif x2 > b: b = x2

            self.draw_line(a, y0, b, y0, color)
            return

        dx11 = x1 - x0
        dy11 = y1 - y0
        dx12 = x2 - x0
        dy12 = y2 - y0
        dx22 = x2 - x1
        dx22 = y2 - y1

        # For upper part of triangle, find scanline crossings for segments
        # 0-1 and 0-2.  If y1=y2 (flat-bottomed triangle), the scanline y2
        # is included here (and second loop will be skipped, avoiding a /0
        # error there), otherwise scanline y1 is skipped here and handled
        # in the second loop...which also avoids a /0 error here if y0=y1
        # (flat-topped triangle).
        if y1 == y2:
            last = y1     # Include y1 scanline
        else:
            last = y1 - 1 # Skip it

        y = y0
        sa = 0
        sb = 0

        while y <= last:
            a = x0 + sa / dy11
            b = x0 + sb / dy12
            sa += dx11
            sb += dx12

            # longhand:
            # a = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            # b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            if a > b: a, b = b, a
            self.draw_line(a, y, b, y, color)
            y += 1

        # For lower part of triangle, find scanline crossings for segments
        # 0-2 and 1-2.  This loop is skipped if y1=y2.
        sa = dx22 * (y - y1)
        sb = dx12 * (y - y0)

        while y <= y2:
            a = x1 + sa / dy22
            b = x0 + sb / dy12
            sa += dx22
            sb += dx12

            # longhand:
            # a = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            # b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            if a > b: a, b = b, a
            self.draw_line(a, y, b, y, color)
            y += 1

        self.__end_write()

    def draw_line(self, x0, y0, x1, y1, color):
        """
        Draw a line using rectangular coordinates.

        @param x0: Start point coordinate (x0-axis).
        @type x0: int
        @param y0: Center point coordinate (y0-axis).
        @type y0: int
        @param x1: Center point coordinate (x1-axis).
        @type x1: int
        @param y1: Center point coordinate (y1-axis).
        @type y1: int
        @param color: A 16-bit color.
        @type color: int
        """
        # Classic Bresenham algorithm
        steep = abs(y1 - y0) > abs(x1 - x0)

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)

        err = dx / 2

        if y0 < y1:
            ystep = 1
        else:
            ystep = -1

        self.__start_write()

        while x0 <= x2:
            if steep:
                self.draw_pixel(y0, x0, color)
            else:
                self.draw_pixel(x0, y0, color)

            err -= dy

            if err < 0:
                y0 += ystep
                err += dx

            x0 += 1

        self.__end_write()

    def draw_pixel(self, x0, y0, color):
        """
        Draw a pixel.

        @param x0: Point coordinate (x-axis).
        @type x0: int
        @param y0: Point coordinate (y-axis).
        @type y0: int
        @param color: A 16-bit color.
        @type color: int
        """
        if not ((x0 >= self._max_x) or (y0 >= self._max_y)):
            self._orient_coordinates(x0, y0)
            self.__start_write()
            self._write_register(self.RAM_ADDR_SET1, x0)
            self._write_register(self.RAM_ADDR_SET2, y0)
            self._write_register(self.GRAM_DATA_REG, color)
            self.__end_write()

    def draw_text(self, x, y, s, color=RGB16BitColor.COLOR_WHITE):
        """
        Draw a text string to the display.

        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param s: The string to draw on the display.
        @type s: str
        @param color: A 16-bit color (default=white).
        @type color: int
        @rtype The position of x after the text.
        """
        currx = x

        for k in range(len(s)):
            currx += self.draw_char(currx, y, s[k], color) + 1

        return currx

    def get_text_width(self, s):
        """
        Get the text width.

        @param s: Text to get the width for.
        @type s: str
        @rtype Return the width of the s argument.
        """
        width = 0

        for k in range(len(s)):
            width += self.get_char_width(s[k])

        return width

    def calculate_rgb_color(self, red, grn, blu):
        """
        ORIGINAL NAME setColor

        Set the color.

        .. note::

          Calculate an RGB 16-bit color from 8-bit RGB components.
          RGB 16 bit = RED 5 bit + GREEN 6 bit + BLUE 5 bit

        @param red: The hex values between: 0x00..0xff
        @type red: int
        @param grn: The hex values between: 0x00..0xff
        @type grn: int
        @param blu: The hex values between: 0x00..0xff
        @type blu: int
        @rtype Return an RGB 16-bit color.
        """
        return (red >> 3) << 11 | (grn >> 2) << 5 | (blu >> 3)

    def split_rgb_color(self, rgb):
        """
        ORIGINAL NAME splitColor

        .. note::

          Calculate 8-bit RGB components from an RGB 16-bit color.

        @param rgb: An RGB 16-bit color.
        @type rgb: int
        @rtype Return a tuple of the RGB 8-bit components, (red, grn, blu).
        """
        red = (rgb & 0b1111100000000000) >> 11 << 3
        grn = (rgb & 0b0000011111100000) >> 5 << 2
        blu = (rgb & 0b0000000000011111) << 3
        return red, grn, blu

    def draw_bitmap(self, x, y, bitmap, w, h, color,
                    bg=RGB16BitColor.COLOR_BLACK, transparent=False,
                    x_bit=False):
        """
        Draw a bitmap image.

        @param x: Point coordinate (x-axis).
        @type x: int
        @param y: Point coordinate (y-axis).
        @type y: int
        @param bitmap: A 2D 16-bit color bitmap image to draw on the display.
        @type bitmap: int
        @param w: Width
        @type w: int
        @param h: Height
        @type h: int
        @param color: A 16-bit color (default=white).
        @type color: int
        @param bg: A 16-bit background.
        @type bg: int
        @param transparent: True = transparent bitmap, False = not transparent.
        @type transparent: bool
        @param x_bit: This indicates that the left most (8th) bit is set.
        @type x_bit: bool
        """
        #drawBitmap(int16_t x, int16_t y, const uint8_t *bitmap, int16_t w,
        #           int16_t h, uint16_t color)
        # 1 self._draw_bitmap(x, y, bitmap, w, h, color, bg, True, False)

        #drawBitmap(int16_t x, int16_t y, uint8_t *bitmap, int16_t w,
        #           int16_t h, uint16_t color)
        # 2 self._draw_bitmap(x, y, bitmap, w, h, color, bg, False, False)

        #drawXBitmap(int16_t x, int16_t y, const uint8_t *bitmap, int16_t w,
        #            int16_t h, uint16_t color)
        # 3 self._draw_bitmap(x, y, bitmap, w, h, color, bg, True, True)

        #drawXBitmap(int16_t x, int16_t y, const uint8_t *bitmap, int16_t w,
        #            int16_t h, uint16_t color, uint16_t bg)
        # 4 self._draw_bitmap(x, y, bitmap, w, h, color, bg, False, True)

        no_auto_inc = False # Flag set when transparent pixel was 'written'.
        byte_width = (w + 7) / 8
        byte = 0
        mask_bit = 0x01 if x_bit else 0x80
        # Adjust window height/width to display dimensions
        # DEBUG ONLY -- DB_PRINT("DrawBitmap.. maxX=%d, maxY=%d", _maxX,_maxY);
        wx0 = 0 if x < 0 else x
        wy0 = 0 if y < 0 else x
        wx1 = (self._max_x if x + w > self._max_x else x + w) - 1
        wy1 = (self._max_y if y + h > self._max_y else y + h) - 1
        wh = wy1 - wy0 + 1

        self._set_window(wx0, wy0, wx1, wy1, AutoIncMode.L2R_TOP_DOWN)
        self.__start_write()

        for j in range((0 if y >= 0 else -y) + wh):
            for i in range(w):
                if i & 7:
                    if x_bit: byte >>= 1
                    else: byte <<= 1
                else:
                    # pgm_read_byte(bitmap + j * byteWidth + i / 8);
                    byte = bitmap[j * byteWidth + i / 8]

                if wx0 <= x + i <= wx1:
                    # Write only if pixel is within window.
                    if no_auto_inc:
                        # There was a transparent area,
                        # set pixel coordinates again
                        self.draw_pixel(x + i, y + j, color)
                        no_auto_inc = False
                    else:
                        self._write_data_16_bit(color)
                elif transparent:
                    no_auto_inc = True # No autoincrement in transparent area!
                else:
                    self._write_data_16_bit(bg)

        self.__end_write()

    def _orient_coordinates(self, x, y):
        if self._orientation == 1:
            y = self._max_y - y - 1
            x, y = y, x
        elif self._orientation == 2:
            x = self._max_x - x - 1
            y = self._max_y - y - 1
        elif self._orientation == 3:
            x = self._max_x - x - 1
            x, y = y, x

        # if self._orientation == 0: We fall through.
        return x, y

    def _set_window(self, x0, y0, x1, y1, mode=AutoIncMode.TOP_DOWN_L2R):
        # Clip to TFT-Dimensions
        x0 = min(x0, self._max_x - 1)
        x1 = min(x1, self._max_x - 1)
        y0 = min(y0, self._max_y - 1)
        y1 = min(y1, self._max_y - 1)
        self._orient_coordinates(x0, y0)
        self._orient_coordinates(x1, y1)

        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0

        # Autoincrement mode
        if self._orientation > 0:
            orient = self._orientation - 1

            try:
                mode = self._MODE_TAB[orient][mode]
            except IndexError as e:
                msg = ("Invalid orientation: {} (0..2) or mode: {} (0..7), "
                       "{}").format(self._orientation, mode, e)
                raise TFTException(msg)

        self.__start_write()
        self._write_register(self.ENTRY_MODE, 0x000 | (mode << 3))
        self._write_register(self.HORIZONTAL_WINDOW_ADDR1, x1)
        self._write_register(self.HORIZONTAL_WINDOW_ADDR2, x0)
        self._write_register(self.VERTICAL_WINDOW_ADDR1, y1)
        self._write_register(self.VERTICAL_WINDOW_ADDR2, y0)

        # Starting position within window and increment/decrement direction
        pos = mode >> 1

        if pos == 0:
            self._write_register(self.RAM_ADDR_SET1, x1)
            self._write_register(self.RAM_ADDR_SET2, y1)
        elif pos == 1:
            self._write_register(self.RAM_ADDR_SET1, x0)
            self._write_register(self.RAM_ADDR_SET2, y1)
        elif pos == 2:
            self._write_register(self.RAM_ADDR_SET1, x1)
            self._write_register(self.RAM_ADDR_SET2, y0)
        elif pos == 3:
            self._write_register(self.RAM_ADDR_SET1, x0)
            self._write_register(self.RAM_ADDR_SET2, y0)

        self.spi_write(self.GRAM_DATA_REG)
        self.__end_write()

    def _reset_window(self):
        self._write_register(self.HORIZONTAL_WINDOW_ADDR1, self.LCD_WIDTH - 1)
        self._write_register(self.HORIZONTAL_WINDOW_ADDR2, 0)
        self._write_register(self.VERTICAL_WINDOW_ADDR1, self.LCD_HEIGHT - 1)
        self._write_register(self.VERTICAL_WINDOW_ADDR2, 0)

    def _write_register(self, reg, data):
        self.spi_write(reg)
        self.spi_write(data)

    def __start_write(self):
        self._write_function_level += 1

        if self._write_function_level == 0:
            self.spi_start_transaction()
            self.digital_write(self._cs, self.LOW) # SPI_CS_LOW();

    def __end_write(self):
        self._write_function_level -= 1

        if self._write_function_level == 0:
            self.digital_write(self._cs, self.HIGH) # SPI_CS_HIGH();
            self.spi_end_transaction()

    def __repr__(self):
        return "<{} object using {}>".format(
            self.__class__.__name__, self.PLATFORM)
