"""
A proxy node
"""

from cryptography.fernet import Fernet
import socket
import argparse
import json
import random
import sys
import base64

CRLF = b"\r\n"
END = CRLF + CRLF


class ProxyClient:
    def __init__(self, connection, debug):
        self.connection = connection
        self.debug = debug
        self.id = None
        self.nextNode = None
        self.key = None

    def setNextNode(self, nextNode):
        # new socket to the next node
        self.nextNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        self.directorySocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
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

    def decrypt(self, message, key):
        # make key into a fernet key
        Fkey = base64.urlsafe_b64encode(key.to_bytes(32, sys.byteorder))
        f = Fernet(Fkey)
        message = f.decrypt(message.encode())
        return message.decode()

    def parseMessage(self, message, clientID):
        if self.debug:
            print("Parsing message")
        message = message.decode()
        message = message.replace(END.decode(), "")
        message = json.loads(message)
        if message["action"]== "setNextNode":
            # save the next node ip and port
            nodeType = message["type"]
            if nodeType == 0:
                # return the next node
                nextNodeIP = message["ip"]
                nextNodePort = message["port"]
                return (nextNodeIP, nextNodePort), nodeType
            else:
                # this is the exit node
                return None,  nodeType
        elif message["action"] == "forward":
            # get the message
            message = message["payload"]
            # TODO: forward the message to the next node as a string
            message = self.decrypt(message, self.clientList[clientID].key)
            if self.debug:
                print("Forwarding message: " + str(message))
            # convert message to json
            clientCon = self.clientList[clientID].connection
            # get the next node
            nextNode = self.clientList[clientID].nextNode
            # send the message to the next node
            nextNode.send(message.encode())
            # send the end to the next node
            nextNode.send(END)
            # wait for the next node to respond
            response = nextNode.recv(1024)
            while END not in response:
                response += nextNode.recv(1024)
            response = response.decode()
            response = response.replace(END.decode(), "")
            response = json.loads(response)
            if self.debug:
                print("Response: " + str(response))
            # TODO: Encrpyt the response packet
            # send the response to the client
            clientCon.send(json.dumps(response).encode())
            clientCon.send(END)
        elif message["action"] == "message":
            # get the message
            msg = self.decrypt(message["payload"], self.clientList[clientID].key)
            # if my node type is 1 then print the message

            print(f"Incoming Message: {msg}")
            if self.nodeType == 1:
                return
            else: # otherwise send the message with a message action
                packet = {
                    "action": "message",
                    "payload": msg
                }
                # send the message to the next node
                self.clientList[clientID].nextNode.send(json.dumps(packet).encode())
                self.clientList[clientID].nextNode.send(END)
        elif message["action"] == "key":
            p = 23
            g = 5
            # retrive the key from the message
            A = int(message["A"])
            if self.debug:
                print("A: " + str(A))
            # Bob chooses a secret integer b = 3, then sends Alice B = gb mod p
            # B = 53 mod 23 = 10
            b = random.randint(1, p-1)
            B = pow(g, b, p)
            if self.debug:
                print("Bob's public key: " + str(B))
            # send the key to the client
            packet = {
                "B": B
            }
            self.clientList[clientID].connection.send(json.dumps(packet).encode())
            self.clientList[clientID].connection.send(END)
            # compute the shared secret key
            s = pow(A, b, p)
            if self.debug:
                print("Shared Key: " + str(s))
            # save the key in the client object
            self.clientList[clientID].key = s

    def intakeMessage(self, connection, clientID=None):
        incoming = connection.recv(1024)
        while END not in incoming:
            incoming += connection.recv(1024)
        if self.debug:
            print("Incoming message: " + incoming.decode())
        return self.parseMessage(incoming, clientID)

    def handleClient(self, client):
        if self.debug:
            print("Client connected")
        # get the next node from the client
        nextNode, nodeType = self.intakeMessage(client.connection, client.id)
        self.nodeType = nodeType

        if self.debug:
            if nextNode is None and nodeType == 1:
                print("This is the exit node")
            else:
                print(f"Next node: {nextNode}")
                print(f"My id: {client.id}")
                print(f"Node type: {nodeType}")
        # if the node is not an exit node
        if nextNode:
            # set the next node for the client
            client.setNextNode(nextNode)
            if self.debug:
                print("Client " + str(client.id) +
                      " connected to " + str(nextNode))

            try:
                client.nextNode.connect(nextNode)
                # send a confirmation to the client
                client.connection.send(json.dumps(
                    {"action": "confirm"}).encode())
                client.connection.send(END)
            except:
                if self.debug:
                    print("Could not connect to next node")
                # send a failure to the client
                client.connection.send(json.dumps(
                    {"action": "failure"}).encode())
                client.connection.send(END)
                # close the connection
                client.connection.close()
                exit(1)
        else:
            if self.debug:
                print(
                    f"Will relay to provided ip and port upon further forward requests")
            # send a confirmation to the client
            client.connection.send(json.dumps(
                {"action": "confirm"}).encode())
            client.connection.send(END)

        # TODO: relay the message and forward response to the client connection
        while True:
            # intake the message
            message = self.intakeMessage(client.connection, client.id)

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
        self.s.bind(('', self.port))
        self.s.listen()

        # accept connections forever
        while True:
            # accept a connection
            connection, address = self.s.accept()

            # create a new client object
            client = ProxyClient(connection, self.debug)

            client.setId(len(self.clientList))

            # add the client to the client list
            self.clientList.append(client)

            self.handleClient(client)


# take in command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run n proxy nodes.')
    # my port number
    parser.add_argument(
        "-p", "--port", help="port number for the proxy node", type=int, default=8080)
    # debug mode
    parser.add_argument(
        "-d", "--debug", help="enable debug mode", action="store_true")
    # directory node port
    parser.add_argument("-np", "--nodedirport",
                        help="port number for the directory node", type=int, default=8081)
    # directory node ip
    parser.add_argument(
        "-ni", "--nodedirip", help="ip address of the directory node", type=str, default="127.0.0.1")

    args = parser.parse_args()
    port = args.port
    debug = args.debug
    directoryPort = args.nodedirport
    directoryIp = args.nodedirip
    # always localhost
    host = "127.0.0.1"

    print("Starting proxy node on port " + str(port))

    # create a proxy node
    proxyNode = ProxyNode(port, host, debug)
    try:
        proxyNode.run(directoryIp, directoryPort)
    except KeyboardInterrupt:
        print("Exiting...")
        # close the socket
        proxyNode.s.close()
        exit(0)

