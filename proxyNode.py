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

    def incomingMessage(self):
        pass

    def outgoingMessage(self):
        pass
        
    def run(self):
        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))
        self.s.listen(self.numNodes)
        self.s.settimeout(1)
      
        if self.debug:
            print("Proxy node listening on port " + str(self.port))
        while True:
            try:
                if self.debug:
                    print("Waiting for connection...")
                # accept a connection
                self.conn, self.addr = self.s.accept()
                self.conn.settimeout(1)
                # receive the data in small chunks and retransmit it
                while True:
                    if self.debug:
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
    # number of nodes
    parser.add_argument("-n", "--nodes", help="number of nodes in the network", type=int, default=3)
    # debug mode
    parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")
    # directory node port
    parser.add_argument("-np", "--nodedirport", help="port number for the directory node", type=int, default=8081)
    # directory node ip
    parser.add_argument("-ni", "--nodedirip", help="ip address of the directory node", type=str, default="127.0.0.1")
    args = parser.parse_args()
    port = args.port
    numNodes = args.nodes
    debug = args.debug
    directory = args.key
    directoryPort = args.nodedirport
    directoryIp = args.nodedirip

    print("Starting proxy node on port " + str(port))

    # create a proxy node
    proxyNode = ProxyNode(port, numNodes, debug)

    proxyNode.run()