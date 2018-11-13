# -*- coding: utf-8 -*-

"""TCP Socket server to communicate Direct-IP messages from Iridium Gateway.

The server is the one who actually communicate with Iridium Gateway, receiving
and transmitting binary messages.
"""

from datetime import datetime
import socket
from io import open
import os.path
import logging
import subprocess
import threading
try:
    import socketserver
except:
    import SocketServer as socketserver

from ..iridiumSBD import valid_isbd, is_truncated, is_inbound, is_outbound


module_logger = logging.getLogger('DirectIP')

def save_isbd_msg(outputdir, client_address, data, t0):
    if not os.path.isdir(os.path.join(outputdir, 'inbox')):
        os.mkdir(outputdir)
        os.mkdir(os.path.join(outputdir, 'inbox'))
    filename = os.path.join(
            outputdir, "inbox", "%s_%s.isbd" % (
                t0.strftime('%Y%m%d%H%M%S%f'), client_address[0]))
    module_logger.debug('Saving isbd message: %s' % filename)
    with open(filename, 'wb') as fid:
        fid.write(data)
    module_logger.debug("Saved: {}".format(filename))
    return filename


def save_corrupted_msg(outputdir, client_address, data, t0):
    if not os.path.isdir(os.path.join(outputdir, 'corrupted')):
        os.mkdir(outputdir)
        os.mkdir(os.path.join(outputdir, 'corrupted'))
    filename = os.path.join(
            outputdir, "corrupted", "%s_%s.isbd" % (
                t0.strftime('%Y%m%d%H%M%S%f'), client_address[0]))
    module_logger.debug('Saving corrupted meessage: %s' % filename)
    with open(filename, 'wb') as fid:
        fid.write(data)
    module_logger.debug("Saved: {}".format(filename))


class DirectIPHandler(socketserver.BaseRequestHandler):
    """A request handler for each transmission.

    Once the DirectIPServer receives a call, it uses DirectIPHandler to deal
    with the transmission.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def __init__(self, request, client_address, server, postProcessing=None):
        self.logger = logging.getLogger('DirectIP.Server.DirectIPHandler')
        self.logger.debug('Initializing DirectIPHandler')
        socketserver.BaseRequestHandler.__init__(
                self, request, client_address, server)

    def handle(self):
        """

        recv() get everything from one sendall(), while readline() will call
        multiple recv() until gets a newline character.
        It is OK to use a buffer of 2048, since the largest message that an
        Iridium can send is 1960 bytes (9522A/B) plus a header of 51 bytes.
        """
        #self.request.settimeout(1)
        self.logger.debug('Receiving a call from %s' % self.client_address[0])
        t0 = datetime.utcnow()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(2048)
        self.logger.debug('Message received, %s bytes' % (len(self.data)))

        while is_truncated(self.data):
            self.logger.debug('Message incomplete. Waiting for the rest')
            self.data += self.request.recv(2048)
            self.logger.debug(
                    'Extending message to %s bytes' % (len(self.data)))

        if not valid_isbd(self.data):
            self.logger.error('Invalid message.')
            save_corrupted_msg(
                    self.server.datadir, self.client_address, self.data, t0)
            return

        #self.data = self.request.recv(1024).strip()
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        #self.data = self.rfile.readline().strip()
        filename = save_isbd_msg(
                self.server.datadir, self.client_address, self.data, t0)

        if is_inbound(self.data):
            # Acknowledgment message
            self.logger.debug('Acknowledging message received.')
            #ack = struct.pack('>cHcHb', b'1', 4, b'\x05', 1, 1)
            ack = b'1\x00\x04\x05\x00\x01\x01'
            s = self.request.send(ack)

            if self.server.postProcessing is not None:
                postProcessing = self.server.postProcessing
                self.logger.debug('External post-processing: {}'.format(
                    postProcessing))
                cmd = (postProcessing, filename)
                self.logger.debug("Running: {}".format(cmd))
                try:
                    output = subprocess.run(cmd,
                                            timeout=60,
                                            check=True,
                                            stdout=subprocess.PIPE)
                    self.logger.debug(
                        'Post-processing output: {}'.format(output.stdout))
                except:
                    self.logger.warn('Failed to run external post-processing')

        elif is_outbound(self.data):
            assert self.server.outbound_address is not None, \
                    "Undefined outbound server."

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server.outbound_address)
            try:
                sock.sendall(self.data)
                response = sock.recv(2048)
                self.logger.debug("Received: {}".format(response))
                self.request.send(response)
            finally:
                sock.close()


class DirectIPServer(socketserver.TCPServer):
    """A TCPServer modified for Direct-IP communication.
    """
    def __init__(self,
                 server_address,
                 datadir,
                 postProcessing=None,
                 outbound_address=None):
        self.logger = logging.getLogger('DirectIP.Server')
        self.logger.debug('Initializing DirectIPServer')

        if outbound_address is not None:
            self.logger.info('Outbound messages will be directed to: %s:%s' %
                    outbound_address)
            self.outbound_address = outbound_address

        if not os.path.exists(datadir):
            self.logger.critical('Invalid datadir: {}'.format(datadir))
            assert os.path.exists(datadir)
        self.datadir = datadir
        self.logger.info('Data directory: {}'.format(datadir))

        if (postProcessing != None) and (not os.path.exists(postProcessing)):
            self.logger.error(
                    "Invalid postProcessing: %s" % postProcessing)
        self.postProcessing = postProcessing

        socketserver.TCPServer.__init__(
                self, server_address, RequestHandlerClass=DirectIPHandler)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.verify_request(
                self, request, client_address)


class ThreadedDirectIPServer(socketserver.ThreadingMixIn, DirectIPServer):
    pass


def runserver(host, port, datadir, postProcessing=None,
              outbound_address=None):
    """Runs a Direct-IP server to listen for messages.

    Initiate DirectIPServer and keep it alive listening for calls.

    Args:
        host (str): Host to be listening as. For example: 127.0.0.1
        port (int): Port to listen on. For example: 10800
        postProcessing (str): Optional command or script to be called for each
            mesage received.  It's better to use a absolute path. A filename
            with the message just received will be the single argument.
    """
    module_logger.debug('Initializing runserver().')
    server = ThreadedDirectIPServer((host, port), datadir, postProcessing,
            outbound_address)
    module_logger.info('Listening as %s:%s' % (host, port))
    try:
        server.serve_forever()
        module_logger.info('Server activated. To interrupt it: Ctrl-C')
    except KeyboardInterrupt:
        module_logger.warn('User terminated server')
        module_logger.debug('=====================')
