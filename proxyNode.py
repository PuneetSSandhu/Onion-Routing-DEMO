"""
A proxy node object.
"""

from multiprocessing.pool import TERMINATE
import socket
import argparse
import json
import threading

CRLF = b"\r\n"
END = CRLF + CRLF

class ProxyClient:
    def __init__(self, connection, debug):
        self.connection = connection
        self.debug = debug
        self.id = None
        self.nextNode = None
    
    def setNextNode(self, nextNode):
        self.nextNode = nextNode
    
    def setId(self, id):
        self.id = id
    
class ProxyNode:
    def __init__(self, port, ip, debug):
        self.port = port
        self.debug = debug
        self.host = ip
        self.clientList = []

    def register(self, port, ip):

        # connect to the directory node
        self.directorySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.directorySocket.connect((ip, port))

        # if can't connect to directory node, exit
        if not self.directorySocket:
            if self.debug:
                print("Could not connect to directory node")
            exit(1)

        # send the port number and ip address to the directory node
        packet = {
            "action": "register",
            "port": self.port,
            "ip": self.host
        }
        self.directorySocket.send(json.dumps(packet).encode())
        self.directorySocket.send(END)

        # disconnect from the directory node
        self.directorySocket.close()
        return

    def parseMessage(self, message):
        message  = message.replace(END, "")
        message = message.decode()
        message = json.loads(message)

        if message["action"] == "setNextNode":
            # save the next node ip and port
            nextNodeIP = message["ip"]
            nextNodePort = message["port"]
            id = message["id"]
            # return the next node
            return (nextNodeIP, nextNodePort), id
        elif message["action"] == "forward":
            # get the id of the client
            id = message["id"]
            # get the message
            message = message["message"]
            # get the next node
            nextNode = self.clientList[id].nextNode
            # send the message to the next node
            self.clientList[id].connection.send(message.encode())
            self.clientList[id].connection.send(END)
            # return the next node
            return nextNode

    def intakeMessage(self, connection):
            
            incoming = connection.recv(1024)
    
            while END not in incoming:
                incoming += connection.recv(1024)
    
            if self.debug:
                print("Incoming message: " + incoming.decode())
    
            return self.parseMessage(incoming)

    def handleClient(self, client):
        # get the next node from the client

        nextNode, id = client.intakeMessage()

        # if the next node is not None
        if nextNode:
            # set the next node for the client
            client.setNextNode(nextNode)
            # set the id of the client
            client.setId(len(self.clientList) - 1)

            # if the next node is not the directory node
            if nextNode != (self.dirNodeIP, self.dirNodePort):
                # connect to the next node
                client.connection.connect(nextNode)

                # send the client id to the next node
                client.connection.send(json.dumps({"action": "id", "id": client.id}).encode())
                client.connection.send(END)

                # start a new thread to handle the client
                thread = threading.Thread(target=self.handleClient, args=(client,))
                thread.start()
            else:
                # start a new thread to handle the client
                thread = threading.Thread(target=self.handleClient, args=(client,))
                thread.start()

    def incomingMessage(self):
        pass

    def outgoingMessage(self):
        pass
        
    def run(self, dirNodeIP, dirNodePort):
        if self.debug:
            print("Proxy node listening on port " + str(self.port))

        # register with the directory node
        self.register(dirNodePort, dirNodeIP)

        # save the directory node ip and port
        self.dirNodeIP = dirNodeIP
        self.dirNodePort = dirNodePort
        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()

        # accept connections forever
        while True:
            # accept a connection
            connection, address = self.s.accept()

            # create a new client object
            client = ProxyClient(connection, self.debug)

            # add the client to the client list
            self.clientList.append(client)

            # start a new thread to handle the client
            thread = threading.Thread(target=self.handleClient, args=(client,))
           
    

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