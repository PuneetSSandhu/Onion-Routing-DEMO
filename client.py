"""
Launches a specified number of nodes
"""
import argparse
import os
import socket
import pickle

class ClientNode:

    def __init__ (self, port, ip, debug):
        self.port = port
        self.debug = debug
        self.host = ip

        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()

    def requestDirectory(self, dirNodeIP, dirNodePort):
        # connect to the directory node
        self.directorySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.directorySocket.connect((dirNodeIP, dirNodePort))

        # for a message to request the directory
        message = "req,\r\r"

        # send the message to the directory node
        self.directorySocket.send(message.encode())

        # receive the directory from the directory node
        directory = pickle.loads(self.directorySocket.recv(1024))

        # close the connection to the directory node
        self.directorySocket.close()

        return directory

    def run(self, dirNodeIP, dirNodePort):
        directory = self.requestDirectory(dirNodeIP, dirNodePort)
        if self.debug:
            print(directory)
        conn, addr = self.s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)



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
    ip = args.ip
    dirIP = args.nodedirip
    dirPort = args.nodedirport

    if debug:
        print("Starting directory node on port " + str(port))

    dirNode = ClientNode(port, ip, debug)    
    dirNode.run(dirIP, dirPort)