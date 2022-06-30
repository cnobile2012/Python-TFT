**********
Python-TFT
**********

Use Python to Connect TFT LCD Displays.

The Python-TFT API will work with versions of python 3.5 and higher MicroPython
and CircuitPython are based on the 3.5 C standard vesion of Python.

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
thirdparty packages not Python-TFT itself. So you may need to install another
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

Building packages for a Raspberry Pi is not absolutly necessary since the
size of the whole git repository is not very much for a RPi. You can build it
if you want which can get you a smaller package.

Below is the basic usage.

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

So building a package for MicroPython would look like this.

.. code-block:: console

   $ ./scripts/create_packages.py -m2fs

You will be confronted by a curses terminal screen. The mouse will work in
the terminal. The screen will look like the following.

.. |Font Chooser| image:: images/TFT-curses.png





Uploading Packages
==================

Raspberry Pi
------------
On a Raspberry PI you can either build a custom package or just checkout
this repository to your RPi.

MicroPython
-----------
