"""
Launches a specified number of nodes
"""
import argparse
import os
import socket
import pickle
import random

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

    def selectNode(self, directory, n):
        # select n nodes from the directory randomly without replacement
        nodeCopy = list(directory)
        selectedNodes = []

        for i in range(n):
            #generate number from 0 to len(nodeCopy)
            rand = int(len(nodeCopy) * (random.random()))
            selectedNodes.append(nodeCopy[rand])
            nodeCopy.pop(rand)
        
        return selectedNodes

    def parseMessage(self, incoming):
        delimiter = ","
        terminate = "\r\r"
        successString = "succ"
        failString = "fail"

        # split the message into a list
        message = incoming.decode().split(",")

        # remove the terminator from the message
        message.pop()

        action = message[0]

        if action == successString:
            return True
        elif action == failString:
            return False
        else: # pass the entire message
            return message



    def run(self, dirNodeIP, dirNodePort, n):
        directory = self.requestDirectory(dirNodeIP, dirNodePort)
        selectedNodes = self.selectNode(directory, n)


        if self.debug:
            print("Selected nodes: " + str(selectedNodes))

       # connect to the first node
        self.nodeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.nodeSocket.connect((selectedNodes[0][0], selectedNodes[0][1]))
        except:
            if self.debug:
                print("Could not connect to node " + str(selectedNodes[0][0]) + ":" + str(selectedNodes[0][1]))
            return
        
        for nodes in selectedNodes[1:]:
            # each proxy node will connect to the next node in the list
            message = "conn," + nodes[0] + "," + str(nodes[1]) + "\r\r"



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
    # Number of nodes
    parser.add_argument("-n", "--numnodes", type=int, default=1, help="number of nodes to chain")

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