**********
Python-TFT
**********

Use Python to Connect TFT LCD Displays.

The Python-TFT API will work with versions of python 3.5 and higher MicroPython
and CircuitPython are based on the 3.5 C standard version of Python.

Building Packages
=================

If you are so inclined to build your own packages then follow the instructions
below. This is only needed if you want to install specific fonts in your
package and prefer not to install them by hand.

Installing Python 3.9
---------------------

First off, though the API itself will work with versions of Python 3.5 and
higher the tests and the build script will only run with versions of Python 3.8
and 3.9, lower and higher version do not work properly. This is mostly due to
third-party packages not Python-TFT itself. So you may need to install another
version before you go further. This will most likely be necessary if you are
building on a Raspberry PI. Follow the instructions below to install version
3.9.13 of Python.

First update and install a few system packages.

.. code-block:: console

  $ sudo apt update && apt upgrade
  $ sudo apt install libssl-dev cargo libsqlite3-dev ncurses-bin \
                     ncurses-base libncurses5-dev

I usually create a directory named *src* in my user directory assuming you also
do the same cd into that directory then execute the commands below.

.. code-block:: console

   $ wget https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tar.xz
   $ tar -xJvf Python-3.9.13.tar.xz
   $ cd Python-3.9.13/
   $ ./configure --enable-optimizations --enable-loadable-sqlite-extensions=yes
   $ sudo make altinstall

With the *altinstall* target in the Makefile Python will be installed in the
*/usr/local* path. As of this writing Python-3.10.4 does not work with
*nosetests* however the build script may work.

Build Platform Packages
-----------------------

Building packages for a Raspberry Pi is not absolutely necessary since the
size of the whole git repository is not very much for a RPi. You can build it
if you want which can get you a much smaller package. Keep in mind that
building packages on any platform will flatten the file structure under the
chip type that you are using. All packages will look more or less the same.
Note that the directory tree below is for a MicroPython package and the font
files are just examples.

.. code-block:: console

   .
   └── ILI9225
       ├── common.py
       ├── compatibility.py
       ├── default_fonts.py
       ├── fonts
       │   ├── BebasNeue_Bold10pt7b.py
       │   ├── FreeMonoBoldOblique12pt7b.py
       │   ├── __init__.py
       │   ├── Org_01.py
       │   └── TomThumb.py
       ├── ili9225.py
       ├── __init__.py
       └── micropython.py

Below is the basic usage of the package creation script.

.. code-block:: console

   $ ./scripts/create_packages.py --help
   usage: create_packages.py [-h] [-a] [-c] [-p] [-m] [-r] [-2] [-3] [-f] [-s] [-F] [-D] [-N]

   Creating packages...

   optional arguments:
     -h, --help           show this help message and exit
     -a, --all            Create all packages.
     -c, --circuitpython  Create a CircuitPython package.
     -p, --computer       Create a Computer package.
     -m, --micropython    Create a MicroPython package.
     -r, --raspi          Create a Raspberry Pi package.
     -2, --ili9225        Create a ILI9225 package.
     -3, --ili9341        Create a ILI9341 package.
     -f, --fonts          Choose which fonts to put in the final packages.
     -s, --strip          Strip comments and non-code white space on the
                          MicroPython and CircuitPython packages.
     -F, --force-strip    Force striping on all packages including the
                          Raspberry Pi and Computer packages.
     -D, --debug          Run in debug mode.
     -N, --noop           Run as if creating, but do nothing.

Building a package for MicroPython would look similar to the following. The
package will build for the *ILI9225* chip the curses screen will appear for
choosing fonts and all doc strings, comments, and extra line-feeds will be
removed to save space on the MCU.

.. code-block:: bash

   $ ./scripts/create_packages.py -m2fs

You will be confronted by a curses terminal screen if you use the *-f* option.
The mouse will work in the terminal. Without the *-f* option no fonts will be
included in your package.

 1. Click the left mouse button or press the Enter key on the *Choose Font(s)*
    button. This will let the mouse work in the left window. The mouse wheel
    can be used to scroll up and down the font files if there are more than
    what can fit on the screen.
 2. The left mouse button is used to choose the fonts you want in your package.
 3. Clicking twice on the *Continue* button will continue with building your
    package.
 4. If you have chosen the wrong packages and want to start over click twice
    on the *Cancel* button and start over again.
 5. If you want to just exit the whole process click twice on the *Exit*
    button.

The "click twice" mentioned above is needed as the first click gets you out of
the left window. Note that the left and right keys also can be used to navigate
the main menu.

.. image:: images/TFT-curses.png
   :height: 100px
   :width: 400px
   :scale: 100%
   :alt: File chooser curses screen.
   :align: center

Uploading Packages
==================

Be sure you are in the root directory of the git repository of this API
that you have cloned to your machine.

Raspberry Pi
------------

On a Raspberry PI you can either build a custom package or just checkout
this repository to your RPi. A built package will work better in a python
virtual environment because it can be copied directly into the VE much easier.

MicroPython
-----------

Create you package as describe above.

.. code-block:: bash

   $ cd build/micropython/
   $ ampy -p /dev/ttyUSB0 put ILI9225

Your device may be different than the one I used. If you type *ampy* with no
arguments you will get a list of the commands *ampy* provides.
