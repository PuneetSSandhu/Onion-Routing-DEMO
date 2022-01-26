"""
Launches a specified number of nodes
"""
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run n proxy nodes.')
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

    # create a node port directory
    nodeDirectory = set(range(port, port + numNodes))

    for i in range(numNodes):
        if debug:
            print("Starting proxy node on port " + str(port + i))
        # run a console command
        os.system("python3 proxyNode.py -p " + str(port + i) + " -n " + str(numNodes) + " -d " + str(debug))
    






