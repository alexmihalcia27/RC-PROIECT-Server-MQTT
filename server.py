import sys
import threading
from connect import *


class Client:
    def __init__(self, conn, addr):
        self.addr = addr
        self.conn = conn
        self.user = None
        self.password = None
        self.id = None
        self.type_of_qos = None
        self.qos_message = []
        self.will_message = None
        self.will_topic = None
        self.keep_alive = None
        self.will_retain = None
        self.topic = []
    def afisare (self):
        return self.conn

class SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.state = False
        self.clients = []
        self.will_topic = None
        self.will_message = ['','','',' ']
        self.topics = {"CpuInfo",
                       "CpuUsage",
                       "MemoryInfo",
                       "DiskInfo"}


    # pornim serverul
    def start(self):
        # Setare socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # https://pubs.opengroup.org/onlinepubs/000095399/functions/setsockopt.html
        self.state = True
        print("Serverul a fost pornit\n")
        self.listenThread = threading.Thread(target=self.listen,
                                              args=())
        self.listenThread.start()



    def listen(self):
        while self.state:
            self.socket.listen()  # serverul ascuta
            (conn, addr) = self.socket.accept()
            #verificam daca este un client nou sau unul vechi
            check = 0
            place_client = 0
            i = 0
            for a in self.clients:
                if a.addr[0] == addr[0] and a.addr[1] == addr[1]:
                    a.conn = conn
                    check = 1
                    place_client = i
                i = place_client + 1
            if check == 0:
                client = Client(conn, addr)

            if check == 0:
                self.THREAD_HANDLE_Clients = threading.Thread(target=self.HANDLE_Clients, args=(client,check))
                self.THREAD_HANDLE_Clients.start()

            else:
                self.THREAD_HANDLE_Clients = threading.Thread(target=self.HANDLE_Clients, args=(self.clients[place_client],check,))
                self.THREAD_HANDLE_Clients.start()

    def HANDLE_Clients(self, client, check):
        while 1:
            data = client.conn.recv(1024)
            print(data)
            #matematica nebuna pe biti
            check_for_enum = struct.unpack('B', data[0:1])[0]
            print(check_for_enum)
            aux = check_for_enum % 16
            check_for_enum = check_for_enum - aux



            control_packet_type = Control_packet_type(check_for_enum)
            print("Tipul pachetului " + str(control_packet_type) )
            for a in self.clients:
                print(a.addr)



            #CONNECT-ul + #CONNACK-ul
            if (control_packet_type == Control_packet_type.CONNECT):
                start_encoding, finish_encoding = decodeSecondByte(data[1:])
                data = data[1 + start_encoding: 1 + start_encoding + finish_encoding]
                client_con, check, text = CONNECT(client, data)
                if (check):
                    self.clients.append(client_con)
                    client.conn.sendall(text)
                else:
                    send(text, client_con)
                    return

            #PUBLISH

            if(check == 1):
                if(control_packet_type == Control_packet_type.PUBLISH):
                    a = struct.unpack('B', data[0:1])[0]
                    biti  =  a
                    aux = a % 16
                    a = a - aux
                    biti = biti - a
                    biti = decode_binary_flag(biti)

                    DUP_flag = biti[4]
                    retain  = biti [7]
                    message = b'\x30'
                    message += data[1:]
                    data = data[1:]
                    topic,data = decode_name(data[1:])
                    for aux in self.clients:
                        if(topic in aux.topic):
                            aux.conn.sendall(message)



                    if(biti[6] == 1 and biti [5] == 0 ):
                        QoS = 1
                        #PUBACK
                        PUBACK_MESSAGE = b'\x40\x02'
                        PUBACK_MESSAGE += (packet_identifier).to_bytes(1, byteorder='big')
                        print("Se trimite mesajul")
                        client.conn.sendall(PUBACK_MESSAGE)

                    if(biti[6]==0 and biti[5] ==1 ):
                        QoS = 2
                        PUBREC_MESSAGE = b'\x50\x02'
                        PUBREC_MESSAGE += (packet_identifier).to_bytes(1, byteorder='big')
                        send(PUBREC_MESSAGE, client)


                if(control_packet_type == Control_packet_type.PUBREC):
                    biti = int(data[0:1])
                    if(biti != 64):
                        print("NU S-A TRIMIS PUBRECUL CORECT")
                    print("Mesajul a ajuns")



                ######PINGRESP#######
                if(control_packet_type == Control_packet_type.PINGREQ):
                    client.conn.sendall(b'\xC0\x00')




                if(control_packet_type == Control_packet_type.PUBREC):
                    biti = int(data[0:1])
                    if(biti == 80):
                        print("Mesaj prost")
                    packet_identifier = data[2:4]
                    PUBREL_MESSAGE = b'\x62\x02'
                    PUBREL_MESSAGE += (packet_identifier).to_bytes(1, byteorder='big')




                if(control_packet_type == Control_packet_type.PUBREL):
                    biti = int(data[0:1])
                    if(biti !=  98):
                        print("MESAJ PROST")
                        #delete client cred
                    packet_identifier = data[2:4]
                    PUBCOMP_MESSAGE = b'\x70\x02'
                    PUBCOMP_MESSAGE += (packet_identifier).to_bytes(1, byteorder='big')

                #SUBSCRIBE




                if (control_packet_type == Control_packet_type.SUBSCRIBE):
                    biti = struct.unpack('B', data[0:1])[0]
                    if(biti != 130):
                        print("Mesaj prost pentru SUBSCRIBE")
                    start_encoding, finish_encoding = decodeSecondByte(data[1:])
                    data = data[1 + start_encoding: 1 + start_encoding + finish_encoding]
                    packet_identifier = data[0:2]
                    data = data[2:]


                    number_of_topics = 1
                    topic , data =decode_name(data)
                    QoS = struct.unpack('B', data[0:1])[0]
                    client.topic.append(topic)
                    client.qos_message.append(QoS)
                    data = data[1:]
                    while(len(data) != 0):
                        topic, data = decode_name(data)
                        QoS = struct.unpack('B', data[0:1])[0]
                        client.topic.append(topic_name)
                        client.type_of_qos.append(qos)
                        data =data[1:]
                        number_of_topics +=1


                #####SUBACK######
                    message_fixedHEADER= b'\x90'
                    message_variableHEADER = packet_identifier
                    message_payload = b''
                    for i in range(number_of_topics):
                        message_payload += b'\x00'
                    lenght =(len(message_variableHEADER) + len(message_payload))
                    lenght = struct.pack('=H', len(message_variableHEADER) + len(message_payload))
                    lenght = lenght[0:1]
                    message_fixedHEADER +=lenght
                    message_fixedHEADER += message_variableHEADER
                    message_fixedHEADER += message_payload
                    client.conn.sendall(message_fixedHEADER)