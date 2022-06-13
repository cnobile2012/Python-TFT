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
    sudo apt install libssl-dev libffi-dev cargo

I usually create a directory named `src` in my user directory assuming you also
do that cd into that directory.





`Install latest Python
<https://raspberrytips.com/install-latest-python-raspberry-pi/>`_

