"""
A proxy node object.
"""

import socket
import argparse
import json
import signal

CRLF = b"\r\n"
END = CRLF + CRLF


class ProxyClient:
    def __init__(self, connection, debug):
        self.connection = connection
        self.debug = debug
        self.id = None
        self.nextNode = None

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

    def signalCleaner(self, signum, frame):
        if self.debug:
            print("Cleaning up")
        for client in self.clientList:
            client.connection.close()
        self.directorySocket.close()
        exit(1)

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

    def parseMessage(self, message, clientID):
        if self.debug:
            print("Parsing message")
        message = message.decode()
        message = message.replace(END.decode(), "")
        message = json.loads(message)
        if message["action"] == "setNextNode":
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
            if self.debug:
                print("Forwarding message: " + str(message))
            # TODO: forward the message to the next node as a string
            # convert message to json
            message = json.dumps(message)
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
        # TODO: relay the message and forward response to the client connection
        while True:
            # intake the message
            message = self.intakeMessage(client.connection, client.id)

    def run(self, dirNodeIP, dirNodePort):
        signal.signal(signal.SIGINT, self.signalCleaner)

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

            client.setId(len(self.clientList))

            # add the client to the client list
            self.clientList.append(client)

            self.handleClient(client)


# take in command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run n proxy nodes.')
    # my host
    parser.add_argument('-i', '--ip', type=str,
                        default='127.0.0.1', help='ip address of the proxy node')
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
    host = args.ip

    print("Starting proxy node on port " + str(port))

    # create a proxy node
    proxyNode = ProxyNode(port, host, debug)
    proxyNode.run(directoryIp, directoryPort)
