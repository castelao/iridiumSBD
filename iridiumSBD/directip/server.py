""" TCP Socket server to receive DirectIP messages from Iridium
"""

from datetime import datetime
import socket
from io import open
import os.path
import logging
import json
import subprocess
try:
    import socketserver
except:
    import SocketServer as socketserver

from ..iridiumSBD import valid_isbd, is_truncated, is_inbound, is_outbound


module_logger = logging.getLogger('DirectIP')
DATADIR = "/home/gs/data/isbd"
assert os.path.isdir(DATADIR)
assert os.path.isdir(os.path.join(DATADIR, 'inbox')
assert os.path.isdir(os.path.join(DATADIR, 'corrupted')


def save_isbd_msg(client_address, data, t0):
    filename = os.path.join(
            DATADIR, "inbox", "%s_%s.isbd" % (
                t0.strftime('%Y%m%d%H%M%S%f'), client_address[0]))
    module_logger.debug('Saving isbd message: %s' % filename)
    with open(filename, 'wb') as fid:
        print("{} wrote:".format(client_address[0]))
        fid.write(data)
    return filename


def save_corrupted_msg(client_address, data, t0):
    filename = os.path.join(
            DATADIR, "corrupted", "%s_%s.isbd" % (
                t0.strftime('%Y%m%d%H%M%S%f'), client_address[0]))
    module_logger.debug('Saving corrupted meessage: %s' % filename)
    with open(filename, 'wb') as fid:
        print("{} wrote:".format(client_address[0]))
        fid.write(data)


class DirectIPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

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

            recv() get everything from one sendall(), while readline() will
              call multiple recv() until gets a newline character.
            It is OK to use a buffer of 2048, since the largest message that
              an Iridium can send is 1960 bytes (9522A/B) plus a header of 51
              bytes.
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
            self.logger.debug('Extending message to %s bytes' % \
                    (len(self.data)))

        if not valid_isbd(self.data):
            self.logger.error('Invalid message.')
            save_corrupted_msg(self.client_address, self.data, t0)
            return

        #self.data = self.request.recv(1024).strip()
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        #self.data = self.rfile.readline().strip()
        filename = save_isbd_msg(self.client_address, self.data, t0)

        if is_inbound(self.data):
            # Acknowledgment message
            self.logger.debug('Acknowledging message received.')
            #ack = struct.pack('>cHcHb', b'1', 4, b'\x05', 1, 1)
            ack = b'1\x00\x04\x05\x00\x01\x01'
            s = self.request.send(ack)

            if self.server.postProcessing is not None:
                postProcessing = self.server.postProcessing
                try:
                    self.logger.debug('External post-processing: %s',
                            postProcessing)
                    cmd = (postProcessing, filename)
                    self.logger.debug("Running: {}".format(cmd))
                    output = subprocess.check_output(cmd)
                    self.logger.debug(
                            'Post-processing output: {}'.format(output))
                except:
                    self.logger.warn('Failed to run external post-processing')

        elif is_outbound(self.data):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            try:
                sock.sendall(self.data)
                response = sock.recv(2048)
                self.logger.debug("Received: {}".format(response))
                self.request.send(response)
            finally:
                sock.close()


class DirectIPServer(socketserver.TCPServer):
    def __init__(self, server_address, postProcessing=None):
        self.logger = logging.getLogger('DirectIP.Server')
        self.logger.debug('Initializing DirectIPServer')
        self.postProcessing = postProcessing
        socketserver.TCPServer.__init__(self,
                server_address, RequestHandlerClass=DirectIPHandler)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.verify_request(
                self, request, client_address)


def runserver(host, port, postProcessing=None):
    server = DirectIPServer((host, port), postProcessing)
    module_logger.info('Listening as %s:%s' % (host, port))
    try:
        server.serve_forever()
        module_logger.info('Server activated. To interrupt it: Ctrl-C')
    except KeyboardInterrupt:
        module_logger.warn('User terminated server')
        module_logger.debug('=====================')
