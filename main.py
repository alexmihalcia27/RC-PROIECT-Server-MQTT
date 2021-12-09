import enum
import socket
import threading
import struct

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





def CONNECT(client, data):
    print(data);



class Client:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr


class SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.state = False
        self.clients = []

    # pornim serverul
    def start(self):
        # Setare socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # https://pubs.opengroup.org/onlinepubs/000095399/functions/setsockopt.html
        self.state = True
        print("Serverul a fost pornit\n")
        self.THREAD_listen = threading.Thread(target=self.listen,
                                              args=()).start()  # dam drumul si la 2 threaduri unul care primeste mesajul si il adauga in clienti
        self.THREAD_HANDLE_Clients = threading.Thread(target=self.HANDLE_Clients,
                                                      args=()).start()  # iar celalat  ce il prelucreaza

    def listen(self):
        self.socket.listen()  # serverul ascuta
        while self.state:
            (conn, addr) = self.socket.accept()
            print("La server s-a concectat " + str(addr))
            client = Client(conn, addr)
            self.clients.append(client)

    def HANDLE_Clients(self):
        while self.state:
            if len(self.clients) != 0:
                for client in self.clients:
                    data = client.conn.recv(1024)
                    print( (str(client.addr)).lstrip('(').lstrip(')')+ "\ta trimis mesajul: " + str(data))
                    control_packet_type = Control_packet_type(struct.unpack('B', data[0:1])[0])
                    print("Tipul pachetului "  +str(control_packet_type))
                    if(control_packet_type == Control_packet_type.CONNECT):
                        print(data)
                        start_encoding, finish_encoding = decodeSecondByte(data[1:])  #in documentatie spune sa incepem de la al doilea parametru
                        data =data[1+start_encoding: 1+start_encoding+ finish_encoding]  #trimitem la decode doar fixed-headerul si payloadul
                        print("ceva")
                        CONNECT(client,data)




if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5003  # am pirmit o eroare dubiosa daca il pun pe 1884
    server = SERVER(host, port)
    server.start()

