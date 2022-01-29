"""
Launches a specified number of nodes
"""
import argparse
import os
import socket

class DirNode:

    def __init__ (self, port, numNodes, ip, debug):
        self.port = port
        self.numNodes = numNodes
        self.debug = debug
        self.host = ip

        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()
        self.nodeDirectory = nodeDirectory

    def run(self):
        if self.debug:
            print("Proxy node listening on port " + str(self.port))

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
    # number of nodes
    parser.add_argument("-n", "--nodes", help="number of nodes in the network", type=int, default=3)
    # debug mode
    parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")

    args = parser.parse_args()
    port = args.port
    numNodes = args.nodes
    debug = args.debug
    ip = args.ip

    # create a node port directory
    nodeDirectory = set(range(port, port + numNodes))

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