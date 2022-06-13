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

First off, though the API will work with versions of Python 3.5 and higher the
tests and the build script will only run with versions of Python 3.8 and 3.9,
lower and higher version do not work properly. This is mostly due to thirdparty
packages not Python-TFT itself. So you may need to install another version
before you go further. This will most likely be necessary if you are building
on a Raspberry PI. Follow the instructions below to install version 3.9.13 of
Python.

First update and install a few system packages.

.. code-block:: console

  sudo apt update && apt upgrade
  sudo apt install libssl-dev cargo libsqlite3-dev

I usually create a directory named *src* in my user directory assuming you also
do the same cd into that directory then execute the commands below.

.. code-block:: console

   wget https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tar.xz
   tar -xJvf Python-3.9.13.tar.xz
   cd Python-3.9.13/
   ./configure --enable-optimizations --enable-loadable-sqlite-extensions=yes
   sudo make altinstall

With the *altinstall* target on the Makefile Python will be installed in the
*/usr/local* path. As of this writing Python-3.10.4 does not work with
nosetests.

