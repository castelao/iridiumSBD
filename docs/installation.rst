.. highlight:: shell

============
Installation
============


Requirements
------------

IridiumSBD is a Python package, thus requiring a running `Python`_ in your machine. It is compatible with Python 2 and 3, but I strongly recommend you to use Python 3 if you can.

IridiumSBD requires the Python package `Click`_. The installation with pip automatically takes care of the requirements, but to install from the source it is necessary to download and install `Click`_ first.

.. _Python: https://www.python.org/
.. _Click: http://http://click.pocoo.org/6/


Stable release
--------------

To install Iridium Short Burst Data, run this command in your terminal:

.. code-block:: console

    $ pip install iridiumSBD

This is the preferred method to install Iridium Short Burst Data, as it will always install the most recent stable release. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for Iridium Short Burst Data can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/castelao/iridiumSBD

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/castelao/iridiumSBD/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/castelao/iridiumSBD
.. _tarball: https://github.com/castelao/iridiumSBD/tarball/master
