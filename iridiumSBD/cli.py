#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command line utilities for IridiumSBD package

This utility allows to access and use the IridiumSBD package resources from
the command line without requiring to explicitly open the Python first. Note
that it still requires Python installed in the running machine.
"""
#    python directip --loglevel=info --logfile=/var/log/directip listen \
#            --host=localhost --port=10800

import logging
import logging.handlers

import click

from .iridiumSBD import IridiumSBD
from .directip.server import runserver


@click.group()
@click.option(
        '--loglevel',
        type=click.Choice(['debug', 'info', 'warn', 'error']),
        default='info')
@click.option(
        '--logfile',
        default=None)
def main(loglevel, logfile):
    """ Utilities for Iridium DirectIP communication
    """
    # create logger with 'directip'
    logger = logging.getLogger('DirectIP')
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)

    if logfile is not None:
        # create file handler which logs even debug messages
        fh = logging.handlers.RotatingFileHandler(
              logfile, maxBytes=(1024**2), backupCount=10)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, loglevel.upper()))
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info('Running DirectIP command line.')


@main.command(name='listen')
@click.option('--host', type=click.STRING)
@click.option('--port', type=click.INT, default=10800)
@click.option('postProcessing', '--post-processing', type=click.STRING,
        help='External shell command to run on received messages.')
def listen(host, port, postProcessing):
    """ Run server to listen for transmissions
    """
    logger = logging.getLogger('DirectIP')
    logger.info('Executing runserver.')
    if host is None:
        logger.critical('Invalid host: "%s"' % host)
        assert host is not None

    logger.debug('Calling server.')
    runserver(host, port, postProcessing)


@main.command(name='dump')
@click.argument('file', type=click.File('rb'))
def dump(file):
    """ Temporary solution to dump an ISBD message
    """
    msg = IridiumSBD(file.read())
    print("protocol_revision: {}".format(msg.attributes['protocol_revision']))
    print("msg_length: {}".format(msg.attributes['msg_length']))
    print("actual_length: {}".format(msg.attributes['actual_length']))
    print("header section")
    for v in msg.attributes['header']:
        print("  {}: {}".format(v, msg.attributes['header'][v]))


if __name__ == '__main__':
    main()
