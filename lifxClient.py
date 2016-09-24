import math

TYPE_POS     = 16 + 8
SEQUENCE_POS = TYPE_POS + 8 + 64
RES_REQ_POS  = SEQUENCE_POS + 8
ACK_REQ_POS  = RES_REQ_POS + 1
TARGET_POS   = ACK_REQ_POS + 1 + 6 + 48
SOURCE_POS   = TARGET_POS + 64
PROTOCOL_POS = SOURCE_POS + 16 + 8
ADDRESS_POS  = PROTOCOL_POS + 12
TAGGED_POS   = ADDRESS_POS + 1
ORIGIN_POS   = TAGGED_POS + 1
SIZE_POS     = ORIGIN_POS + 2 + 16

class LifxMessage:

    def __init__(self, source, sequence):

        protocol = 1024
        data = 0

        data |= sequence << SEQUENCE_POS
        data |= source   << SOURCE_POS
        data |= protocol << PROTOCOL_POS
        data |= 1        << ADDRESS_POS

        self.data = data

    def get_packet(self, msg_type, payload=None, payload_size=0, target=0, ack_req=0, res_req=0):

        tagged = 0
        if target == 0:
            tagged = 1

        packet = self.data
        packet |= msg_type << TYPE_POS
        packet |= res_req  << RES_REQ_POS
        packet |= ack_req  << ACK_REQ_POS
        packet |= target   << TARGET_POS
        packet |= tagged   << TAGGED_POS

        size = 36
        packet |= size     << SIZE_POS
        if payload != None:
            size = payload_size
            packet += size << SIZE_POS

            packet = packet << (size)*8
            packet |= payload

        return packet

"""
if __name__ == '__main__':
    msg = LifxMessage(0xAAAAAAAA, 0xAA)
    discovery_packet = msg.get_packet(101)

    print('{0:x}'.format(discovery_packet))
    #print('012345678901234567890123456789012345678901234567890123456789012345678901')
"""

# Send UDP broadcast packets

MYPORT = 56700
BCAST_IP = '255.255.255.255'

import sys, time
from socket import *

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

msg = LifxMessage(0xAAAAAAAA, 0xAA)

discover = (msg.get_packet(2)).to_bytes(42, byteorder='big')
on = (msg.get_packet(21, payload=0xFFFF00000000, payload_size=6, res_req=1)).to_bytes(42, byteorder='big')
off = (msg.get_packet(21, payload=0x000000000000, payload_size=6, res_req=1)).to_bytes(42, byteorder='big')

color = 0x0000
brightness = 0
while 1:
    _payload = 0x000000ffffFFFFffff00000000

    _payload |= color << 80
    color += 0x00FF
    color = color % 0xFFFF

    packet = msg.get_packet(102, payload=_payload, payload_size=13).to_bytes(49, byteorder='big')
    #packet = msg.get_packet(101).to_bytes(36, byteorder='big')

    s.sendto(packet, (BCAST_IP, MYPORT))

    time.sleep(0.05)
    print('{0:x}'.format(color), end='\r')


