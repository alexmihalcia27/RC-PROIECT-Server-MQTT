import enum
import struct
import socket
from server import *
class Control_packet_type(enum.Enum):
    RESERVED = 0
    CONNECT = 16
    CONNACK = 32
    PUBLISH = 48
    PUBACK = 64
    PUBREC = 80
    PUBREL = 96
    PUBCOMP = 112
    SUBSCRIBE = 128
    SUBACK = 144
    UNSUBSCRIBE = 160
    UNSUBACK = 176
    PINGREQ = 192
    PINGRESP = 208
    DISCONNECT = 224
    Reserved = 240


def decodeSecondByte(byte):
    ####decodificare########
        multiplier = 1
        val = 0
        i = 0
        binary = int.from_bytes(byte[i:i + 1], "big")
        while True:
            val += (binary & 127) * multiplier
            if binary & 128 == 0:
                break
            multiplier = multiplier * 128
            i += 1
            binary = int.from_bytes(byte[i:i + 1], "big")
        return i + 1, val


def decode_binary_flag(flag):
    flags = str(format(flag, 'b'))
    ret = []
    if len(flags) != 8:
        for i in range(8 - len(flags)):
            ret.append(0)
    for i in range(len(flags)):
        ret.append(int(flags[i]))
    return ret


def decode_name(data):
    index  = struct.unpack('>H',data[0:2])[0]
    index = int(index)
    name = data[2: 2+index]
    name = name.decode('utf-8')
    return name , data[2+index:]


def send(MESSAGE, client):
    TCP_IP = client.addr[0]
    TCP_PORT = 5006
    BUFFER_SIZE = 1024.
    s = socket. socket(socket. AF_INET, socket. SOCK_STREAM)
    s. connect((TCP_IP, TCP_PORT))
    s. send(MESSAGE)





