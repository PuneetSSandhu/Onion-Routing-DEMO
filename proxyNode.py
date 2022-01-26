"""
A proxy node object.
"""

import socket
import argparse

class ProxyNode:
    def __init__(self, port, numNodes, debug):
        self.port = port
        self.numNodes = numNodes
        self.debug = debug

    def connectToNode(self, nodeId):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((nodeId, self.port))
        self.conn.settimeout(1)
        return self.conn
        
    def run(self, nodeDirectory):
        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))
        self.s.listen(self.numNodes)
        self.s.settimeout(1)
        self.nodeDirectory = nodeDirectory
        self.nodeDirectory.add(self.port)
        print("Proxy node listening on port " + str(self.port))
        while True:
            try:
                print("Waiting for connection...")
                # accept a connection
                self.conn, self.addr = self.s.accept()
                self.conn.settimeout(1)
                # receive the data in small chunks and retransmit it
                while True:
                    print("Receiving data...")
                    data = self.conn.recv(1024)
                    if not data:
                        break                                                                
                    self.conn.sendall(data)
            except socket.timeout:
                pass
            except:
                self.conn.close()
                raise
    

# take in command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run n proxy nodes.')
    # my port number
    parser.add_argument("-p", "--port", help="port number for the proxy node", type=int, default=8080)
    # port to connect to
    parser.add_argument("-c", "--connect", help="port number to connect to", type=int)
    # number of nodes
    parser.add_argument("-n", "--nodes", help="number of nodes in the network", type=int, default=3)
    # debug mode
    parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")
    args = parser.parse_args()
    port = args.port
    numNodes = args.nodes
    debug = args.debug
    nodeId = args.connect

    # make a node directory
    nodeDirectory = set()

    print("Starting proxy node on port " + str(port))
    # create a proxy node
    proxyNode = ProxyNode(port, numNodes, debug)

    if (nodeId != None):
        print("Connecting to node on port " + str(nodeId))
        proxyNode.connectToNode(nodeId)

    proxyNode.run(nodeDirectory)