# -*- coding: utf-8 -*-

import struct
from struct import calcsize, unpack_from
import binascii
from datetime import datetime, timedelta
from collections import OrderedDict


class Message(object):
    def __init__(self, content):
        self.content = content
        self.offset = 0

    def __str__(self):
        return str(self.content)

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        """
            Avoids to convert to string when requesting only 1 item,
              like msg[0]
        """
        if (type(item) is int) and (item != -1):
            item = slice(item, item+1)
        return self.content[self.offset:][item]

    def consume(self, fmt):
        size = calcsize(fmt)
        output = unpack_from(fmt, self.content, offset=self.offset)
        self.offset += size
        if len(output) == 1:
            return output[0]
        else:
            return output


def parse_MO_header(msg):
    assert msg[0:1] == b'\x01'
    cfg = OrderedDict([
        ('IEI', '>c'),
        ('length', '>H'),
        ('CDR_reference', '>I'),
        ('IMEI', '>15s'),
        ('session_status', '>B'),
        ('MOMSN', '>H'),
        ('MTMSN', '>H'),
        ('session_epoch', '>I')
        ])

    header = {}
    for v in cfg:
        header[v] = msg.consume(cfg[v])

    header['IMEI'] = header['IMEI'].decode()
    header['session_datetime'] = \
        datetime(1970, 1, 1, 0, 0, 0) + \
        timedelta(seconds=header['session_epoch'])
    return header


def parse_MO_location(msg):
        assert msg[0:1] == b'\x03'

        packformat = '>cHBBHBHI'
        #block_len = struct.calcsize(packformat)
        #if block_len > len(msg):
        #    return
        m = msg.consume(packformat)
        #m = struct.unpack_from(packformat, msg)
        assert m[0] == b'\x03'

        location = {}
        location['IEI'] = m[0]
        location['length'] = m[1]
        # 0=N,E; 1=N,W; 2=S,E; 3=S,W
        location['orient'] = m[2]
        location['lat_deg'] = m[3]
        location['lat_min'] = m[4] * 1e-3
        location['lon_deg'] = m[5]
        location['lon_min'] = m[6] * 1e-3
        location['CEP_radius'] = m[7]

        location['latitude'] = location['lat_deg'] + location['lat_min'] / 60.
        if location['orient'] in (2, 3):
            location['latitude'] *= -1
        location['longitude'] = location['lon_deg'] + location['lon_min'] / 60.
        if location['orient'] in (1, 3):
            location['longitude'] *= -1

        return location


def parse_MO_payload(msg):
    assert msg[0:1] == b'\x02'
    cfg = OrderedDict([
        ('IEI', '>c'),
        ('length', '>H')
        ])
    payload = {}
    for v in cfg:
        payload[v] = msg.consume(cfg[v])

    #packformat= '>cH'
    #block_len = struct.calcsize(packformat)
    #if block_len > len(msg):
    #    return
    #m = struct.unpack_from(packformat, msg)
    #self.msg.offset = offset
    #m = self.msg.consume('>cH')
    #assert m[0] == b'\x02'

    #payload = {}
    #payload['IEI'] = m[0]
    #payload['length'] = m[1]
    #payload['data'] = msg[3:3+m[1]]
    payload['data'] = msg[:payload['length']]
    msg.offset += payload['length']

    return payload


def parse_MO_confirmation(msg):
        assert msg[0:1] == b'\x05'
        packformat = '>cHb'
        block_len = struct.calcsize(packformat)
        if block_len > len(msg):
            return
        m = msg.consume(packformat)

        confirmation = {}
        confirmation['IEI'] = m[0]
        confirmation['length'] = m[1]
        confirmation['status'] = m[2]

        return confirmation


def parse_MT_confirmation(msg):
        assert msg[0:1] == b'\x44'
        packformat = '>cHI15sIh'
        block_len = struct.calcsize(packformat)
        if block_len > len(msg):
            return
        #m = struct.unpack_from(packformat, msg)
        m = msg.consume(packformat)
        #self.msg.offset = offset
        #m = self.msg.consume('>cH')

        confirmation = {}
        confirmation['IEI'] = b'\x44'
        confirmation['length'] = m[1]
        confirmation['unique_client_msg_id'] = m[2]
        confirmation['IMEI'] = m[3]
        confirmation['auto_id_reference'] = m[4]
        confirmation['status'] = m[5]

        return confirmation


class IridiumSBD(object):
    """Parse an Iridium SBD messge from DirectIP.

    Iridium transmit SBD messages through DirectIP using its own binary format.
    This class gives a comprehensible object.

    Attributes:
        header: A dictionary with the section header of an ISBD message.
        payload: A dictionary with the section payload of an ISBD message.
        confirmation: A dictionary with the section confirmation of an ISBD
            message.
        mtype: Message type, MO or MT.

    One can run this as:

    >>> isbd = IridiumSBD(msg)
    >>> isbd.header # {'IEI': ..., 'length': ...}
    >>> isbd.payload
    >>> isbd.confirmation

    >>> isbd.mtype # 'MO' | 'MT'

    >>> isbd.decode() # Parse the binary message
    >>> isbd.encode() # Encode proprieties into a binary message
    """
    def __init__(self, msg=None):
        """Initialize an IridiumSBD object.

        Args:
            msg (byte): A binary ISBD message (optional). If given, runs
                load(msg).
        """
        self.mtype = None
        if msg is not None:
            self.load(msg)

    def __str__(self):
        return self.attributes

    def load(self, msg):
        """Parse an Iridium SBD binary message.

        Args:
            msg (byte): A binary ISBD message (optional). If given, runs
                load(msg).

        The input (msg) is the Iridium SBD message in its original
            binary format.

        Big endian
        Protocol Revision: 1
        Data segmented into information elements (IEs)
                IEI ID      1
                IEI length  2 (content length, i.e. after the 3 initial bytes)
                IEI content N
        Information Elements Identifiers (IEI)
                MO Header IEI                 0x01
                MO Payload IEI                0x02
                MO Location Information IEI   0x03
                MO Confirmation IEI           0x05

        What is the syntax for the MO Receipt Confirmation???
        """
        assert msg[0:1] == b'\x01', "I can only handle Protocol Revision 1"

        self.msg = Message(msg)

        self.attributes = {}
        self.attributes['protocol_revision'] = self.msg.consume('>c')
        self.attributes['msg_length'] = self.msg.consume('>H')
        self.attributes['actual_length'] = len(self.msg)

        while len(self.msg[:]) > 0:
            if self.msg[0] == b'\x01':
                self.attributes['header'] = parse_MO_header(self.msg)
                self.mtype = 'MO'
            elif self.msg[0] == b'\x02':
                self.payload = parse_MO_payload(self.msg)
            elif self.msg[0] == b'\x03':
                self.attributes['location'] = parse_MO_location(self.msg)
            elif self.msg[0] == b'\x05':
                self.attributes['confirmation'] = parse_MO_confirmation(
                        self.msg)
                self.mtype = 'MO'
            elif self.msg[0] == b'\x41':
                self.mtype = 'MT'
            elif self.msg[0] == b'\x42':
                # Identical to MO payload, but size is limited to 1890 bytes.
                print('MT Payload')
            elif self.msg[0] == b'\x44':
                self.attributes['confirmation'] = parse_MT_confirmation(
                        self.msg)
                self.mtype = 'MO'
            elif self.msg[0] == b'\x46':
                print('MT message Priority')
            else:
                assert False, "Unkown section"

    def payload_as_hex(self):
        return binascii.hexlify(self.payload['data'])

    def payload_as_base64(self):
        return binascii.b2a_base64(self.payload['data'])


def is_truncated(msg):
    """ Check if an ISBD message is incomplete

        Protocol revision of ISBD messages are defined in the first byte as
          a character.

        Revision 1: The size of the rest of the message is given in the
          following two bytes, as an unsigned short integer.

        Input: The binary ISBD message itself.
    """
    if len(msg) < 3:
        return True

    rev, size = unpack_from('>cH', msg)
    if (rev == b'\x01') and (len(msg) < size + 3):
        return True


def is_inbound(msg):
    assert msg[:1] == b'\x01', "Sorry, can only handle revision \\x01"
    if msg[3:4] in [b'\x01', b'\x02', b'\x03', b'\x04']:
        return True


def is_outbound(msg):
    assert msg[:1] == b'\x01', "Sorry, can only handle revision \\x01"
    if msg[3:4] in [b'\x41', b'\x42', b'\x46']:
        return True


def message_type(msg):
    assert msg[:1] == b'\x01', "Sorry, can only handle revision \\x01"
    if msg[3:4] in [b'\x01', b'\x02', b'\x03', b'\x04', b'\x05']:
        return 'MO'
    elif msg[3:4] in [b'\x41', b'\x42', b'\x44', b'\x46']:
        return 'MT'


def valid_isbd(msg):
    """ Fast check if message looks like a valid ISBD
    """
    if is_truncated(msg):
        return False

    rev, size = unpack_from('>cH', msg)
    if rev != b'\x01':
        return False

    if len(msg) != (size + 3):
        return False

    return True


def dump(file, imei):
    """Show isbd message header as text
    """
    msg = IridiumSBD(file.read())
    if imei:
        print(msg.attributes['header']['IMEI'])
        return

    print("protocol_revision: {}".format(msg.attributes['protocol_revision']))
    print("msg_length: {}".format(msg.attributes['msg_length']))
    print("actual_length: {}".format(msg.attributes['actual_length']))
    print("header section")
    for v in msg.attributes['header']:
        print("  {}: {}".format(v, msg.attributes['header'][v]))
