from ajutor import *
import struct


def CONNACK(client):

    fixedheader = b'\x20\x02'
    variabileheader = b'\x00'
    if(client.user != 'user' or client.password != 'password'):
        variabileheader += b'\x04'
        check = 0
    else :
        variabileheader += b'\x00'
        check = 1
    fixedheader += variabileheader

    return check, fixedheader



def CONNECT(client, data):

    lenght_protocol_name =(struct.unpack('>H',data[0:2])[0])
    if lenght_protocol_name!= 4:
        print("Lungimea numelui gresita!!")
    protocol_name = data[2:2+lenght_protocol_name]
    data = data[2+lenght_protocol_name:]                                                                #update_data
    protocol_name = protocol_name.decode("utf-8")

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
        client.type_of_qos = 0
    elif(flags[4]== 1 and flags[3] ==0):
        client.type_of_qos = 1
    elif(flags[4]==0 and flags[3] == 1):
        client.type_of_qos = 2

    if(flags[2]!=0):
        client.will_retain = flag[2]

    keep_alive = (struct.unpack('>H', data[0:2])[0])
    data = data[2:]
    #update data
    if keep_alive:
        client.keep_alive = keep_alive

    ####
    ###  incepe payloadul de aici
    ###


    #luam id ul clientului
    id_name , data = decode_name(data)
    client.id = id_name

    #verificam daca are topic
    if(flags[5]):
        will_topic, data  =decode_name(data)
        will_message, data = decode_name(data)
        client.will_topic = will_topic
        client.will_message = will_message



    #verificam numele

    if(flags[0]):
        name, data = decode_name(data)
        client.user = name

    #verificam parola
    if(flags[1]):
        password ,data = decode_name(data)
        client.password = password



    check ,text = CONNACK(client)


    return  client, check,text
