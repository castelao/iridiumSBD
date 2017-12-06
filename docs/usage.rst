=====
Usage
=====

----------
Quickstart
----------

To obtain help in the terminal::

    iridiumSBD --help

To obtain help for a specific sub-command, for example, running a server::

    iridiumSBD listen --help
    
To initialize a direct-IP server::

    iridiumSBD --logfile=/var/logs/direcip.log --loglevel=info listen --host=YOUR.IP.ADDRESS --port=10800

Running a direct-IP server with a post-processing procedure::

    iridiumSBD --logfile=/var/logs/directip.log --loglevel=info listen --host=YOUR.IP.ADDRESS --port=10800 --post-processing=/home/myself/bin/my_postprocessing_script.sh

To run the server even after logout::

    nohup iridiumSBD listen --host=YOUR.IP.ADDRESS &

To parse an isbd (binary) message saved in a file::

    iridiumSBD dump your_file.isbd


-------
General
-------

Iridium Short Burst Data (ISBD) can be transmitted by email or Direct-IP. At this point, the IridiumSBD Python Package only handles Direct-IP messages.

---------
Direct IP
---------

The Direct-IP communications are exchanged using a TCP/IP socket, between the Iridium Gateway and the user server. 
It thus requires a server listening 24/7.
IridiumSBD server takes that job on receiving Mobile Originated (MO) messages and transmitting Mobile Terminated (MT) messages.

For MO messages, IridiumSBD server saves the full binary transmission in a local file, and if given a post-processing script, it is triggered on every transmission with the binary file as an argument.

.. figure:: figs/IridiumSBD_MO_direct-IP.pdf
   :align: center
   :alt: Flowchart IridiumSBD MO message

   Flowchart of IridiumSBD server receiving an MO message.

Once the IridiumSBD is installed, it includes the command line: iridiumSBD. The minimal call to run it is::

    iridiumSBD listen --host=YOUR.IP.ADDRESS

where YOUR.IP.ADDRESS is the IP that the server will be listening on. If behind a NAT/Gateway, use the internal IP.

The default port recommended by the Iridium Gateway is 10800. If using a different one, specify with '--port=10800', like::

    iridiumSBD --loglevel=debug listen --host=YOUR.IP.ADDRESS --port=10800

The log level can be selected with '--loglevel=info', like::

    iridiumSBD --loglevel=debug listen --host=YOUR.IP.ADDRESS --port=10800

that is a good example for tests, where a lot of information will be saved. For operational it is probably fine to use info or warn level.

To save logs in local files, so in case of problems one can investigate its history, include the logfile argument. If not given, the log does not save it, but only show in the standard output, usually the screen. An example to save logs in files is::

    iridiumSBD --logfile=/var/logs/directip.log --loglevel=info listen --host=YOUR.IP.ADDRESS --port=10800
 
The goal or IridiumSBD Python package is to only communicate binary packages. To allow customization, it is possible to define a command, or script, to be called every time a new message is received. For instance, if the server is called as::

    iridiumSBD listen --host=YOUR.IP.ADDRESS --post-processing=/home/myself/bin/my_postprocessing_script.sh

every new message will be saved in a local file. Right after the file is saved, the post-processing is triggered with the binary filename (with absolute path) as argument. Let's assume that the file created was '/data/example1.isbd', thus one should expect::

    /home/myself/bin/my_postprocessing_script.sh /data/example1.isbd

The post-processing script can be anything, so each user can apply it's custom procedure, which could be to archive the binary message, inject in a SQL database or process it.
