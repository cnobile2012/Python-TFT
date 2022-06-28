#
# File_chooser.py
#
# This curses app provides code to choose a group of files that can
# be processed later in an appilication.
#
# The terminal screen should be at least 84 characters wide and wider if
# font file names are longer than 28 characters.
#

import curses
import os
import sys

from curses import panel
from curses.textpad import rectangle


class ExitData:

    def __init__(self):
        # False means continue with the build and True means just exit.
        self._exit_status = False
        # The font files to use in build process.
        self._files = []

    @property
    def status(self):
        return self._exit_status

    @status.setter
    def status(self, value):
        self._exit_status = value

    @property
    def files(self) -> list:
        return self._files

    @files.setter
    def files(self, flist: list):
        self._files = flist


class Menu:
    LR = 0
    UD = 1

    def __init__(self, stdscr):
        """
        The last keyword x is not needed if used in the Left Right
        configuration.
        """
        self._stdscr = stdscr
        self._menuwin = {}

    def display(self, win_id, items, *, h=-1, w=-1, y=0, x=0, direction=UD,
                color=None, title=None, str_y=-1, str_x=-1, init_mouse=True):
        max_y, max_x = self._stdscr.getmaxyx()
        idx_quit = [(idx, item) for idx, item in enumerate(items)
                    if item[0] == 'q']

        if idx_quit:
            _quit = idx_quit[0][1]
            items.pop(idx_quit[0][0])

        num_items = len(items)

        if direction == Menu.UD:
            height = num_items + 2 if h == -1 else h
            width = max([len(item[0]) for item in items]) + 5 if w == -1 else w
            key_comp_1 = curses.KEY_UP
            key_comp_2 = curses.KEY_DOWN
        else: # direction == self.LR:
            height = 3 if h == -1 else h
            width = max_x - 9 if w == -1 else w
            key_comp_1 = curses.KEY_LEFT
            key_comp_2 = curses.KEY_RIGHT

        if color is None:
            curses.init_pair(1000, curses.COLOR_WHITE, curses.COLOR_BLACK)
            color = curses.color_pair(1000)

        item_crds = [(item[0], len(item[0])) for item in items]
        win = self._create_window(win_id, height, width, y, x, color)

        if title is not None:
            self._display_title(win_id, title, str_y, str_x, color)

        if init_mouse:
            curses.mousemask(curses.ALL_MOUSE_EVENTS |
                             curses.REPORT_MOUSE_POSITION)
            curses.mouseinterval(0)

        position = 0
        loop = True
        click = False

        while loop:
            coords = self._display_menu(win_id, items, position, direction,
                                        str_y, str_x, color)
            key = win.getch()

            if key in [curses.KEY_ENTER, 10, 13] or click:
                click = False
                loop = items[position][1]()
            elif key == key_comp_1:
                position = (position + num_items - 1) % num_items
            elif key == key_comp_2:
                position = (position + num_items + 1) % num_items
            elif idx_quit and chr(key).lower() == 'q':
                loop = _quit[1]()
            elif key == curses.KEY_MOUSE:
                id, _x, _y, z, bstate = curses.getmouse()
                in_win = win.enclose(y, x)

                if in_win:
                    if (bstate in (curses.BUTTON1_PRESSED,
                                   curses.BUTTON1_RELEASED)):
                        for mpos, (name, item_len) in enumerate(item_crds):
                            yy, xx = coords[name]

                            if xx <= (_x-6) < (item_len + xx):
                                position = mpos
                                click = True
                                break

        if init_mouse: curses.mousemask(0)
        win.keypad(False)

    def _display_menu(self, win_id, items, position, direction, str_y, str_x,
                      color):
        win = self._menuwin[win_id]
        win.refresh()
        total_pos = 2
        coords = {}

        for idx, item in enumerate(items):
            if (idx) == position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL

            if direction == Menu.LR:
                y = 1 if str_y == -1 else str_y + 3
                x = total_pos if str_x == -1 else str_x + total_pos + 5
                msg = f"{item[0]}"
            else: # direction == Menu.UD:
                y = idx + 1 if str_y == -1 else str_y + 3
                x = 1 if str_x == -1 else str_x
                msg = f"{idx + 1}. {item[0]}"

            win.addstr(y, x, msg, color | mode | curses.A_BOLD)
            coords[item[0]] = (y, x - 1)

            if direction == Menu.LR:
                total_pos += len(item[0]) + 2

        return coords

    def _create_window(self, win_id, height, width, y, x, color):
        win = self._menuwin.setdefault(
            win_id, self._stdscr.subwin(height, width, y, x))

        win.clear()
        win.attron(color | curses.A_BOLD)
        win.border()
        win.attroff(color | curses.A_BOLD)
        win.keypad(True)
        pan = panel.new_panel(win)
        panel.update_panels()
        return win

    def _display_title(self, win_id, title, str_y, str_x, color):
        if str_y != -1 or str_x != -1:
            title = title if isinstance(title, (tuple, list)) else (title,)
            title_len = max([len(t) for t in title])

            for idx, t in enumerate(title):
                self._menuwin[win_id].addstr(str_y + idx, str_x, t,
                                             color | curses.A_BOLD)


class FileChooser(Menu):

    def __init__(self, stdscr, path=None, exit_data=None):
        super().__init__(stdscr)

        if path is None:
            print("You dumb ass, you need to pass in a path to font files.")
        else:
            self.exit_data = exit_data
            self.start(stdscr, path)

    def get_font_file_list(self, path):
        if not os.path.exists(path):
            raise IOError(f"The {path} does not exist.")

        files = [f for f in os.listdir(path)
                 if f.endswith('.py') and not f.startswith('__')]
        return [[num, f, curses.A_NORMAL]
                for num, f in enumerate(files, start=1)]

    def start(self, stdscr, path):
        self._files_left = self.get_font_file_list(path)
        self._files_right = []
        cur = curses.curs_set(0)
        max_y, max_x = stdscr.getmaxyx()
        widest = max([len(f) for num, f, mode in self._files_left])
        self._meta = {
            'global': {'stdscr': stdscr, 'max_y': max_y, 'max_x': max_x,
                       'widest': widest},
            'win_right': {},
            'win_left': {}
            }
        self.setup_color_pairs()
        self.draw_outer_box()
        self.draw_left_window(files=self._files_left)
        self.draw_right_window()
        self.draw_title_and_menu()
        stdscr.refresh()
        curses.curs_set(cur)

    def setup_color_pairs(self):
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        self.YELLOW_BLACK = curses.color_pair(1)
        self.BLUE_BLACK = curses.color_pair(2)
        self.GREEN_BLACK = curses.color_pair(3)
        self.RED_BLACK = curses.color_pair(4)

    def draw_outer_box(self):
        stdscr = self._meta['global']['stdscr']
        max_y = self._meta['global']['max_y']
        max_x = self._meta['global']['max_x']
        start_y, start_x = 1, 3
        stdscr.attron(self.BLUE_BLACK|curses.A_BOLD)
        rectangle(stdscr, start_y, start_x, max_y - start_y, max_x - start_x)
        stdscr.attron(self.BLUE_BLACK|curses.A_BOLD)

    def draw_title_and_menu(self):
        stdscr = self._meta['global']['stdscr']
        max_y = self._meta['global']['max_y']
        max_x = self._meta['global']['max_x']
        title = "Choose Fonts"
        x = max_x // 2 - len(title) // 2
        stdscr.addstr(2, x, title, curses.A_BOLD)

        menu_items = [
            ("Choose Font(s)", self._chooser),
            ("Continue", self._continue),
            ("Cancel", self._cancel),
            ("Exit", self._exit),
            ("q", self._exit),
            ]
        kwargs = {
            'y': 3,
            'x': 5,
            'direction': Menu.LR,
            'color': self.BLUE_BLACK
            }
        self.display('main', menu_items, **kwargs)

    def draw_left_window(self, files=[], start=0):
        widest = self._meta['global']['widest']
        win = self._meta['win_left'].get('win')
        num_files = len(files[start:])

        if win:
            width = self._meta['win_left']['width']
            height = self._meta['win_left']['height']
        else:
            stdscr = self._meta['global']['stdscr']
            max_y = self._meta['global']['max_y']
            y, x = 6, 5
            width = widest + 9
            height = max_y - 7
            win = stdscr.subwin(height, width, y, x)
            win.attron(self.GREEN_BLACK|curses.A_BOLD)
            win.border()
            win.attroff(self.GREEN_BLACK|curses.A_BOLD)
            self._meta['win_left'] = {
                'win': win, 'width': width, 'height': height
                }

        end = num_files if num_files < (height - 2) else height - 2 + start

        for idx, (num, f, mode) in enumerate(files[start:end], start=1):
            win.addstr(idx, 1, f"{num:>4d}. {f:<{widest}s}",
                       mode|self.GREEN_BLACK)

        win.refresh()

    def draw_right_window(self, files=[]):
        widest = self._meta['global']['widest']
        win = self._meta['win_right'].get('win')
        num_files = len(files)

        if win:
            width = self._meta['win_right']['width']
            height = self._meta['win_right']['height']
        else:
            stdscr = self._meta['global']['stdscr']
            max_y = self._meta['global']['max_y']
            max_x = self._meta['global']['max_x']
            y, x = 6, max_x - (widest + 13)
            width = widest + 9
            height = max_y - 7
            win = stdscr.subwin(height, width, y, x)
            win.attron(self.YELLOW_BLACK|curses.A_BOLD)
            win.border()
            win.attroff(self.YELLOW_BLACK|curses.A_BOLD)
            self._meta['win_right'] = {
                'win': win, 'width': width, 'height': height
                }

        end = num_files if num_files < (height - 2) else height - 2

        for idx, (num, f, mode) in enumerate(files[:end], start=1):
            win.addstr(idx, 1, f"{idx:>4d}. {f}",
                       self.YELLOW_BLACK|curses.A_BOLD)

        win.refresh()

    def _chooser(self):
        left = self._meta['win_left']['win']
        height = self._meta['win_left']['height']
        right = self._meta['win_right']['win']
        left.keypad(True)
        scroll = 0
        file_len = len(self._files_left)
        mode = curses.A_NORMAL # *** TODO *** Fix hightlighting or remove it.

        while True:
            key = left.getch()

            if key == curses.KEY_MOUSE:
                id, x, y, z, bstate = curses.getmouse()
                in_win = left.enclose(y, x)

                if in_win: # *** TODO *** Add an else to see if we can get out.
                    if (bstate in (curses.BUTTON1_PRESSED,
                                   curses.BUTTON1_RELEASED)):
                        yy = y - 7 + scroll
                        cfile = self._files_left[yy]
                        flist = [item[1] for item in self._files_right]

                        if cfile[1] not in flist:
                            self._files_right.append(cfile)
                            self.draw_right_window(self._files_right)
                    elif bstate == curses.BUTTON4_PRESSED:
                        scroll += -1 if scroll > 0 else 0
                        self.draw_left_window(files=self._files_left,
                                              start=scroll)
                    elif bstate == 2097152:
                        scroll += 1 if scroll < (file_len - height + 2) else 0
                        self.draw_left_window(files=self._files_left,
                                              start=scroll)
                else: # Break out with mouse click outside of the left window.
                    break
            else:
                break # Break out with a keyboard key.

        left.keypad(False)
        return True

    def _continue(self):
        self.exit_data.files = [item[1] for item in self._files_right]
        return False

    def _cancel(self):
        self._files_right = []
        right = self._meta['win_right']['win']
        right.clear()
        self._meta['win_right']['win'] = None
        self.draw_right_window()
        return True

    def _exit(self):
        return False


if __name__ == '__main__':
    import pprint

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("The path arguments is missing.")
        sys.exit(1)

    ed = ExitData()
    curses.wrapper(FileChooser, path=path, exit_data=ed)
    print(f"Exit status: {ed.status}")
    print("Font files to process:")
    pprint.pprint(ed.files)
    sys.exit(0)
