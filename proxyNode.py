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
        self.chains = {}
        self.connections = []

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

    def incomingMessage(self, data, conn):
        connect = "conn" # add the provided node's connection to the chain
        exitNode  = "fin" # register my connection but dont add anything to my chain (exit node)
        forward = "forw" # forward a message to the next node or provided ip and port
        delimiter = "," # delimiter for the message
        terminate = "\r\r" # terminate the message
        successString = "succ" # success message
        failString = "fail" # failure message

        message = data.decode()
        message = message.split(delimiter)
        # remove the null byte
        message.pop()

        action = message[0]

        if action == connect:
            # retrive the ip and port of the node to connect to
            ip = message[1]
            port = int(message[2])

            # connect to the node
            nextNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                nextNode.connect((ip, port))

                # add the new connection to the list of connections
                self.connections.append(conn)
                # add a empty chain to the list of chains with the new connection
                self.chains[conn] = []
                # add the new connection to the chain of the current connection
                self.chains[conn].append(nextNode)

            except:
                if self.debug:
                    print("Could not connect to node " + str(ip) + ":" + str(port))
                conn.send(failString.encode())
                conn.send(delimiter.encode())
                conn.send(terminate.encode())

                return

            # send a response to the client
            conn.send(successString.encode())
            conn.send(delimiter.encode())
            conn.send(terminate.encode())
        elif action == forward:
            # forward the message to the next node in the chain
            nextNode = self.chains[conn][0]
            
            # if I am the last node in the chain, send the message to the destination and wait for a response
            if len(self.chains[conn]) == 0:
                nextNode.send(data)
                
                # collect the response till the end of the message
                response = b''
                while True:
                    data = nextNode.recv(1024)
                    if not data:
                        break
                    response += data
                
                # send the response to the client
                conn.send(response)
                return
            else:
                # forward the message to the next node in the chain
                nextNode.send(data)

                # wait for a response
                response = b''
                while True:
                    data = nextNode.recv(1024)
                    if not data:
                        break
                    response += data
                
                # send the response to the client
                conn.send(response)
                return

        elif action == exitNode:
            # register the connection but dont add anything to the chain
            self.connections.append(conn)
            self.chains[conn] = []

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