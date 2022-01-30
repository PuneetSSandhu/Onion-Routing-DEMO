"""
Launches a directory node
"""
import argparse
import os
import socket
import pickle

class DirNode:

    def __init__ (self, port, numNodes, ip, debug):
        self.port = port
        self.numNodes = numNodes
        self.debug = debug
        self.host = ip
        self.dir = set()

        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()
        self.nodeDirectory = nodeDirectory

    def register(self, incoming):
        ip = incoming[1]
        port = int(incoming[2])
        self.dir.add((ip, port))

    def run(self):
        if self.debug:
            print("Directory Node listening on port " + str(self.port))
        # listen for incoming connections forever
        while True:
            conn, addr = self.s.accept()
            with conn:
                if self.debug:
                    print('Connected by', addr)
                while True:
                    # receive data from the client until the client send a null byte
                    incoming = conn.recv(1024)
                    message = incoming.decode()

                    while message.split(",")[-1] != "\r\r":
                        incoming = conn.recv(1024)
                        message += incoming.decode()
                    
                    # parse the message
                    message = message.split(",")
                    # remove the null byte
                    message.pop()

                    if message[0] == "req": # request for node directory
                        # send the list of nodes to the client
                        conn.send(pickle.dumps(self.dir))
                        conn.send(",\0".encode())
                        if self.debug:
                            print("Sent node directory")
                    elif message[0] == "reg": # register a node
                        self.register(message)
                        if self.debug:
                            print("Registered node: " + str(message[1]) + ":" + str(message[2]))
                    else:
                        if self.debug:
                            print("Unknown message received: " + message)
                    break




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run n proxy nodes.')
    # my host 
    parser.add_argument('-i', '--ip', type=str, default='127.0.0.1', help='ip address of the proxy node')
    # my port number
    parser.add_argument("-p", "--port", help="port number for the proxy node", type=int, default=8081)
    # number of nodes
    parser.add_argument("-n", "--nodes", help="number of nodes in the network", type=int, default=0)
    # debug mode
    parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")

    args = parser.parse_args()
    port = args.port
    numNodes = args.nodes
    debug = args.debug
    ip = args.ip

    # create a node port directory
    nodeDirectory = set()

    # defug string
    if debug:
        debugString = "--debug"
    else:
        debugString = ""
    if numNodes > 0:
        for i in range(numNodes):
            if debug:
                print("Starting proxy node on port " + str(port + i))
            # run a console command
            os.system("python3 proxyNode.py -p " + str(port + i) + " -n " + str(numNodes) + " " + debugString + " " + str(port + numNodes + 1) + " &")
    else: 
        print("Starting directory node on port " + str(port))

        dirNode = DirNode(port, numNodes, ip, debug)    
        dirNode.run()

    





