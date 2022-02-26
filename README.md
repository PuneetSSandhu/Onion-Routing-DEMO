# LAB INSTRUCTIONS

## Requirements

Direct or ssh access to the DH lab machines.

## Part 1: Making friends

### Step 1:

Clone this repo :)

> Skip to Part 2 if you have no friends or are doing this at home... alone :(

### Step 2:

Look to your left

### Step 3:

Look to your right

> These non-virual people are your new friends

Try to do this lab activity in groups of 4 or 5.

## Part 2: Getting into the lab

### Step 1: Start a directory node

You need a directory node. Look at the help prompt from `dirNode.py`.

> `python3 dirNode.py -h`

Have the person at the start of your seating arrangement start a directory node and request the IP address from them.

> `ifconfig` on the lab machines

### Step 2: Start a couple proxy nodes

Now you need a few proxy nodes. Look at the help prompt from `proxyNode.py`.

> `python3 proxyNode.py -h`

Start at least 3 proxy nodes and wait for them to connect to the directory node (No crashes).

### Step 3: Get a client running

Now you need a single client node. Look a the help prompt from `client.py`.

> `python3 clientNode.py -h`

This will build the onion route for you. By default a client will try to start a route with one proxy node. Use the argument `-n <path_len>` to make the path length at least 3 nodes long. You will see lots of traffic if this works correctly and a prompt to input a message.
Start sending some messages and observe. Try running with different numbers of proxy nodes too.

## Lab Questions:

### Q1: Longer routes

Try passing messages through longer onion routes (more proxy nodes). What do you notice about the latency? Get a basic time reading, maybe add some time stamps in the code after a the client sends a messages and the proxy relays receive them. If all else fails you can try using your phone's as a stop watch.

### Q2: Message encryption

Assume that the destination you are accessing doesn't support end-to-end encryption. When passing the message through the onion route, can any of the nodes see the direct message? If any of the nodes can see the traffic, suggest a potential fix.

### Q3: Deanonymizing

By default, Tor creates an onion route with 3 nodes between the client and the destination. When passing a message through the onion relay, can any of the nodes determine both the source and destination of these messages? Which who communicates directly with who (client, guard, middle, exit, destination)?

## Lab Submission

Submit a txt file or pdf with your answers.

## Lab Help

> Did \_\_\_ node stall or crash?

Of course it did! We expected this! Due to time constraints we were unable to set up all the error checking and proper port handling when unexpected behaviour or erros occur.

Just close all nodes and try again from the beginning using different ports.

# Onion-Routing-DEMO

A demo of onion routing principals in a one way message sending application.

### Demonstrate onion routing with python scripts

> https://en.wikipedia.org/wiki/Onion_routing

# DISCLAIMER

This is a ~~quick~~ and dirty script. It WILL crash I promise!
