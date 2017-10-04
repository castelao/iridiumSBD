=====
Usage
=====

To use Iridium Short Burst Data in a project::

    import iridiumSBD
    
To initialize the server::

    isbd listen --logpath=/home/gs/logs --loglevel=info listen --host=YOUR.IP.ADDRESS --port=10800

To parse an isbd (binary) message saved in a file::

    isbd dump your_file.isbd
