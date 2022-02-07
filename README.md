# LAB INSTRUCTIONS
## 

## Part 1: Making friends
### Step 1:
Clone this repo :)
> Skip to Part 2 if you have no firends or are doing this at home... alone :(
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

This will build the onion route for you. By default it will start one proxy node. You will see lots of traffic if this works correctly and a prompt to input a message.
Start sending some messages and observe. Try running with different numbers of proxy nodes too.

## Lab Questions:
### Q1: Longer routes
Try passing messages through longer onion routes (more proxy nodes). What do you notice about the latency? (Get a basic time reading, maybe add some time stamps in the code.)

### Q2: Message encryption
Assume that the destination you are accessing doesn't support end-to-end encryption. When passing the message through the onion route, can any of the nodes see the direct message?

### Q3: Deanonymizing
By default, Tor creates an onion route with 3 nodes between the client and the destination. When passing a message through the onion relay, can any of the nodes determine both the source and destination of these messages?


## Lab Help

> Did ___ node stal or crash?

Of course it did! We expected this! Due to time constraints we were unable to set up all the error checking and proper port handling when unexpected behaviour or erros occur.

Just close all nodes and try again from the beginning using different ports.

# Onion-Routing-DEMO
A demo of onion routing principals.

## The History of TOR
* The idea of the Onion router was developed by the United States Naval Research Lab employees for use in protectred communications online for US intelligence
* The TOR project was started in 2005 after the reseach lab released the code for TOR
## Use Cases of TOR
* To browse the dark web
* The use of tor is most notiable when wanting to browse the internet without having your ip address shared with the website
While TOR can hide your ip, it can still be found if the packet itself has your ip
* The format of the packets sent can be anything which can allow sites to trace you without you knowing
## Functionality of TOR
* The ISP will see the traffic sent to the entry node and the desitnation service will see the ip address of the exit node
* There is a 3 node chain with encription for each layer to unpack
* Websites can be hosted as an onion services which probvide access only though the onion router
> This services may act as a fouth trusted node which also has an encripted connection to the exit node rather than being sent the packet unencripted as packets to normal sited would be sent.
* You can connect to the tor network without the browser using the standalone tor service which uses **Socks5 proxy**
## Handshake
* When a client connects to TOR network 

# Demo

### Demonstrate onion routing with python scripts

> https://en.wikipedia.org/wiki/Onion_routing

# DISCLAIMER

This is a ~~quick~~ and dirty script. It WILL crash I promise!