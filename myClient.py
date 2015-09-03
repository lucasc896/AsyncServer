#!/usr/bin/env python
import socket as sk
from sys import argv

if len(argv) > 1:
    mesg = argv[1]
else:
    mesg = "Hey Mum!"

BUFSIZE = 4096

socks = [sk.socket(sk.AF_INET, sk.SOCK_STREAM),sk.socket(sk.AF_INET, sk.SOCK_STREAM)]
print socks
serverAddress = ('localhost', 6666)
for sock in socks:
    print "> Trying to connect to server on %s (port: %s)" % serverAddress
    sock.connect(serverAddress)
    print "> Connected to", serverAddress

for msg in [mesg, "i'm ok.\n"]:
        
    for sock in socks:
        print "Sending", msg
        sock.sendall(msg)
    
    for sock in socks:
        msg = sock.recv(BUFSIZE)
        print "Received: %s" % msg
        if not msg:
            sock.close()