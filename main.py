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





def CONNECT(client, data):
    #acum luam fiecare byte si descifram mesajul
    #https://docs.python.org/3/library/struct.html pentru struct unpack
    lenght_protocol_name =(struct.unpack('>H',data[0:2])[0])
    if lenght_protocol_name!= 4:
        print("Lungimea numelui gresita!!")
        return 0
    protocol_name = data[2:2+lenght_protocol_name]
    data = data[2+lenght_protocol_name:]                                                                #update_data
    protocol_name = protocol_name.decode("utf-8")


    #print(prtocol_name =struct.unpack( '!6s', data[2:lenght_protocol_name]).decode("utf-8"))
    #verificam numele protocolului
    if protocol_name != 'mqtt' and protocol_name != 'MQTT':
      print("Nume protocol gresit")
      return 0





    protocol_lvl =struct.unpack('>b',data[0:1])[0]
    #verificam protocol lvl

    if(protocol_lvl!=4):
        print("Protocol lvl not 4")
        return 0
    data = data[1:]         #update data
    flag = struct.unpack('>B', data[0:1])[0]
    data =data[1:]          #update data
    flags = decode_binary_flag(flag)

    #verificare bit reserved
    if( flags[7]!=0):
        print("Bit rezerved pe 1 ")
        return 0

    if(flags[6]== 0 ):
        #presupunem ca este 1 ca sa nu ne complicam momentan
        print("face ceva")




        # verificam ce fel de qos avem
    if(flags[4]==flags[3]==0):
        print("Folosim qos 0")
    elif(flags[4]== 1 and flags[3] ==0):
        print("Folosim qos 1")
    elif(flags[4]==0 and flags[3] == 1):
        print("Folosim qos 2")


    if(flags[2]!=0):
        print("Fara will-retain")

    keep_alive = (struct.unpack('>H', data[0:2])[0])
    data = data[2:]
    #update data
    if not(keep_alive):
        print("nu are keep_alive")
    ####
    ###  incepe payloadul de aici
    ###


    #luam id ul clientului
    id_name , data = decode_name(data)

    #verificam daca are topic
    if(flags[5]):
        will_topic, data  =decode_name(data)
        will_message, data = decode_name(data)
    #verificam numele

    if(flags[0]):
        name, data = decode_name(data)
        if(name != "user"):
            return 0
    #verificam parola
    if(flags[1]):
        password ,data = decode_name(data)
        if(password!="password"):
            return 0

    return 1





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
                                              args=()).start()  # dam drumul la thread

    def listen(self):
        self.socket.listen()  # serverul ascuta
        while self.state:
            (conn, addr) = self.socket.accept()
            print("La server s-a concectat " + str(addr))
            client = Client(conn, addr)
            self.clients.append(client)
            self.THREAD_HANDLE_Clients = threading.Thread(target=self.HANDLE_Clients,
                                                          args=()).start()

    def HANDLE_Clients(self):
        while self.state:
            if len(self.clients) != 0:
                for client in self.clients:
                    data = client.conn.recv(1024)
                    print( (str(client.addr)))
                    control_packet_type = Control_packet_type(struct.unpack('B', data[0:1])[0])
                    print("Tipul pachetului "  +str(control_packet_type))
                    if(control_packet_type == Control_packet_type.CONNECT):
                        print("----------------------")
                        print(data)
                        print("----------------------\n\n")
                        start_encoding, finish_encoding = decodeSecondByte(data[1:])  #in documentatie spune sa incepem de la al doilea parametru
                        data =data[1+start_encoding: 1+start_encoding+ finish_encoding]  #trimitem la decode doar fixed-headerul si payloadul
                        check = CONNECT(client,data)
                        if(check):
                            print("\nClientul s-a conectat la server")
                            #aici trimite serverul mesaj catre client




if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5004  # am pirmit o eroare dubiosa daca il pun pe 1884
    server = SERVER(host, port)
    server.start()

