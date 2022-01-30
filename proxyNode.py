"""
A proxy node object.
"""

import socket
import argparse
import pickle

class ProxyNode:
    def __init__(self, port, ip, debug):
        self.port = port
        self.debug = debug
        self.host = ip


    def register(self, port, ip):
        register = "reg"
        delimiter = ","
        terminate = "\r\r"
        # connect to the directory node
        self.directorySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.directorySocket.connect((ip, port))

        # if can't connect to directory node, exit
        if not self.directorySocket:
            if self.debug:
                print("Could not connect to directory node")
            exit(1)

        # send the port number and ip address to the directory node
        self.directorySocket.send(register.encode())
        self.directorySocket.send(delimiter.encode())
        self.directorySocket.send(self.host.encode())
        self.directorySocket.send(delimiter.encode())
        self.directorySocket.send(str(self.port).encode())
        self.directorySocket.send(delimiter.encode())
        self.directorySocket.send(terminate.encode())

        # disconnect from the directory node
        self.directorySocket.close()
        return

    def incomingMessage(self):
        pass

    def outgoingMessage(self):
        pass
        
    def run(self, dirNodeIP, dirNodePort):
        if self.debug:
            print("Proxy node listening on port " + str(self.port))

        # register with the directory node
        self.register(dirNodePort, dirNodeIP)
        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()

        # accept connections forever
        while True:
            conn, addr = self.s.accept()
            with conn:
                if self.debug:
                    print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)
    

# take in command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run n proxy nodes.')
    # my host 
    parser.add_argument('-i', '--ip', type=str, default='127.0.0.1', help='ip address of the proxy node')
    # my port number
    parser.add_argument("-p", "--port", help="port number for the proxy node", type=int, default=8080)
    # debug mode
    parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")
    # directory node port
    parser.add_argument("-np", "--nodedirport", help="port number for the directory node", type=int, default=8081)
    # directory node ip
    parser.add_argument("-ni", "--nodedirip", help="ip address of the directory node", type=str, default="127.0.0.1")

    args = parser.parse_args()
    port = args.port
    debug = args.debug
    directoryPort = args.nodedirport
    directoryIp = args.nodedirip
    host = args.ip

    print("Starting proxy node on port " + str(port))

    # create a proxy node
    proxyNode = ProxyNode(port, host, debug)
    proxyNode.run(directoryIp, directoryPort)