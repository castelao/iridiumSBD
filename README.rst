**Archived** : This is not active anymore for a long time. I'm keeping it since it might be a helpful reference, but there is no intention on maintaining it. This was a pilot project at IDG-SIO. Around 2017-2018, I developed another solution using Rust instead, so this Python package has not been used since that. This is a nice proof of concept but I found a latency up to O[100] miliseconds, which was occasionaly an issue.
I don't recommend using this for production.
You might be interested in checking out https://github.com/castelao/DirectIP.

=========================
Iridium SBD communication
=========================

.. image:: https://img.shields.io/pypi/v/isbd.svg
        :target: https://pypi.python.org/pypi/isbd

.. image:: https://img.shields.io/travis/castelao/isbd.svg
        :target: https://travis-ci.org/castelao/isbd

.. image:: https://readthedocs.org/projects/isbd/badge/?version=latest
        :target: https://isbd.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Communication system for Iridium Short Burst Data Service.

A python package to handle direct IP communications with Iridium gateway.

The goal here is to organize it as a standalone Python package with the objective to communicate binary data with Iridium Gateway. It does not try to understand the data being transmitted/received, but that task should be done by another resource. As a python package it is easier to install and update on different machines. With a small and specific objective it is easier to write tests and maintain it.

This is part of a bigger project for IDG communication system with remote instruments as Spray and SOLO.


Alternatives
------------

Other Python packages related to ISBD:

* http://xed.ch/project/isbd/  (Chris X Edwards)
* https://github.com/gadomski/sbd (Pete Gadomski)
