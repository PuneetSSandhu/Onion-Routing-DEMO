"""
Launches a directory node
"""
import argparse
import os
import socket
import json
import signal

CRLF = b"\r\n"
END = CRLF + CRLF

class DirNode:

    def __init__ (self, port, numNodes, ip, debug):
        self.port = port
        self.numNodes = numNodes
        self.debug = debug
        self.host = ip
        self.dir = []

        # start a socket listening for incoming connections
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((ip, port))
        self.s.listen()

    def signalCleaner(self, signum, frame):
        if self.debug:
            print("Cleaning up")
        self.s.close()
        exit(0)

    def register(self, message):
        ip = message["ip"]
        port = int(message["port"])
        # check if the node is already registered
        for node in self.dir:
            if node[0] == ip and node[1] == port:
                return
        # add the node to the directory
        self.dir.append((ip, port))

    def run(self):
        signal.signal(signal.SIGINT, self.signalCleaner)
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
                    while END.decode() not in message:
                        message += incoming.decode()
                        incoming = conn.recv(1024)

                    # remove the END from the message
                    message = message.replace(END.decode(), "")
                    
                    # the packet in a python dictionary
                    message = json.loads(message)
                    if message["action"] == "request": # request for node directory
                        # send the list of nodes to the client
                        if self.debug:
                            print("Sending directory to client : " + str(self.dir))
                        packet = {
                            "action": "directory",
                            "nodes": self.dir
                        }
                        conn.send(json.dumps(packet).encode())
                        conn.send(END)

                        if self.debug:
                            print("Sent node directory")
                    elif message["action"] == "register": # register a node
                        # check if all the required keys are present
                        if "ip" in message and "port" in message:
                            self.register(message)
                        else:
                            if self.debug:
                                print("Invalid registration message")
                        if self.debug:
                            print("Registered node: " + message["ip"] + ":" + str(message["port"]))
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

    # defug string
    if debug:
        debugString = "--debug"
    else:
        debugString = ""

    print("Starting directory node on port " + str(port))

    dirNode = DirNode(port, numNodes, ip, debug)    
    try:
        dirNode.run()
    except KeyboardInterrupt:
        print("Cleaning up")
        dirNode.s.close()
        exit(0)

    





