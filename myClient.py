#!/usr/bin/env python
import socket as sk
from sys import argv
from time import sleep

if len(argv) > 1:
    mesg = argv[1]
else:
    mesg = "Hey Mum!"

BUFSIZE = 4096

# how many different sockets/clients
socks = [sk.socket(sk.AF_INET, sk.SOCK_STREAM) for i in range(3)]

serverAddress = ('localhost', 6666)

for sock in socks:
    # print "> Trying to connect to server on %s (port: %s)" % serverAddress
    sock.connect(serverAddress)
    print "> Connected to", serverAddress

for i in range(1): #how many rounds of messages
    for msg in ["one", "two", "three\n"]:
            
        for sock in socks:
            print "Sending", mesg+msg
            sock.sendall(mesg+msg)
            sleep(1.8)
        
    for sock in socks:
        msg = sock.recv(BUFSIZE)
        print "Received: %s" % msg
