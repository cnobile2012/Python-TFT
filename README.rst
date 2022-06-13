**********
Python-TFT
**********

Use Python to Connect TFT LCD Displays.








Building Packages
=================

If you are so inclined to build your own packages then follow the instructions
below. This is only needed if you want to install specific fonts in your
package and prefer not to install them by hand.

First off the build script will only run on versions of Python of 3.8 and
greater. So you may need to install at least that version before you go
further. This will most likely be necessary if you are building on a Raspberry
PI. At the time of this writing I installed version 3.10.4.

.. code-block:: console

  sudo apt update && apt upgrade
  sudo apt install libssl-dev cargo libsqlite3-dev

I usually create a directory named `src` in my user directory assuming you also
do the same cd into that directory. With the `altinstall` target on the
Makefile Python will be installed in the `/usr/local` path. As of this writing
Python-3.10.4 does not work with nosetests.

.. code-block:: console

   wget https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tar.xz
   tar -xJvf Python-3.9.13.tar.xz
   cd Python-3.9.13/
   ./configure --enable-optimizations --enable-loadable-sqlite-extensions=yes
   sudo make altinstall




`Install latest Python
<https://raspberrytips.com/install-latest-python-raspberry-pi/>`_

