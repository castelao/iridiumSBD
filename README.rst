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
