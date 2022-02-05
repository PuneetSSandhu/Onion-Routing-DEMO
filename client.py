"""
Launches a specified number of nodes
"""

import argparse
import os
import socket
import random
import json
import signal

CRLF = b"\r\n"
END = CRLF + CRLF


class ClientNode:

    def __init__(self, port, ip, debug):
        self.port = port
        self.debug = debug
        self.host = ip
        self.keys = []

        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()

    def signalCleaner(self, signum, frame):
        if self.debug:
            print("Cleaning up")
        self.nodeSocket.close()
        self.s.close()
        exit(0)

    def parseMessage(self, incoming):
        # remove the END from the message
        incoming = incoming.decode().replace(END.decode(), "")
        packet = json.loads(incoming)

        if packet["action"] == "directory":
            # the packet in a python dictionary
            return packet["nodes"]
        elif packet["action"] == "conn":
            return packet["ip"], int(packet["port"])
        elif packet["action"] == "confirm":
            return True
        elif packet["action"] == "fail":
            return False
        else:
            return None

    def intakeMessage(self, connection):

        try:
            incoming = connection.recv(1024)

            while END not in incoming:
                incoming += connection.recv(1024)

            if self.debug:
                print("Incoming message: " + incoming.decode())

            return self.parseMessage(incoming)
        except:
            if self.debug:
                print("Error receiving message")
            return None

    def requestDirectory(self, dirNodeIP, dirNodePort):
        # connect to the directory node
        self.directorySocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.directorySocket.connect((dirNodeIP, dirNodePort))
        except:
            if self.debug:
                print("Could not connect to directory node " +
                      str(dirNodeIP) + ":" + str(dirNodePort))
            exit(1)

        # for a message to request the directory
        message = {
            "action": "request"
        }

        # send the message to the directory node
        self.directorySocket.send(json.dumps(message).encode())
        self.directorySocket.send(END)

        # receive the directory from the directory node
        directory = self.intakeMessage(self.directorySocket)

        # close the connection to the directory node
        self.directorySocket.close()

        return directory

    def selectNode(self, directory, n):
        # select n nodes from the directory randomly without replacement
        nodeCopy = directory.copy()
        selectedNodes = []

        for i in range(n):
            # generate number from 0 to len(nodeCopy)
            rand = int(len(nodeCopy) * (random.random()))
            selectedNodes.append((nodeCopy[rand][0], nodeCopy[rand][1]))
            nodeCopy.pop(rand)

        return selectedNodes

    def run(self, dirNodeIP, dirNodePort, n):
        signal.signal(signal.SIGINT, self.signalCleaner)
        # get the directory from the directory node
        directory = self.requestDirectory(dirNodeIP, dirNodePort)
        if n > len(directory):
            print(
                "Number of nodes requested is greater than the number of nodes in the directory")
            exit(1)

        selectedNodes = self.selectNode(directory, n)

        if self.debug:
            print("Selected nodes: " + str(selectedNodes))

       # connect to the first node
        self.nodeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.nodeSocket.connect((selectedNodes[0][0], selectedNodes[0][1]))
        except:
            if self.debug:
                print("Could not connect to node " +
                      str(selectedNodes[0][0]) + ":" + str(selectedNodes[0][1]))
            return

        selectedNodes.append(None)
        for node in selectedNodes[1:]:
            # number of wrappers is index(node) - 1
            payload = None
            # check if the node is the last node
            if node == None:
                payload = {
                    "action": "setNextNode",
                    "type": 1
                }
            else:
                payload = {
                    "action": "setNextNode",
                    "ip": node[0],
                    "port": node[1],
                    "type": 0
                }

            # create wrapper message
            for i in range(selectedNodes.index(node)-1):
                message = payload.copy()
                payload = {
                    "action": "forward",
                    "payload": message
                }
            if self.debug:
                print("\n\n------------------------------------------------------\n\n")
                print("Sending message: " + str(payload))

            # send the message to the node
            self.nodeSocket.send(json.dumps(payload).encode())
            self.nodeSocket.send(END)

            # TODO: Negotiate the secret key

            # wait for a reply from the node
            reply = self.intakeMessage(self.nodeSocket)

            if not reply:
                print("No reply from node")
                exit(1)

        # TODO: Listen for incoming messages


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
    # Number of nodes
    parser.add_argument("-n", "--numnodes", type=int,
                        default=1, help="number of nodes to chain")

    args = parser.parse_args()
    port = args.port
    debug = args.debug
    ip = args.ip
    dirIP = args.nodedirip
    dirPort = args.nodedirport
    numNodes = args.numnodes

    if debug:
        print("Starting directory node on port " + str(port))

    dirNode = ClientNode(port, ip, debug)
    dirNode.run(dirIP, dirPort, numNodes)
