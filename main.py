from server import *

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5006
    server = SERVER(host, port)
    server.start()

