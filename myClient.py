#!/usr/bin/env python
import socket as sk
# from sys import argv

# if len(argv) > 1:
#     msg = argv[1]
# else:
#     msg = "Hey Mum!"

BUFSIZE = 4096

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
serverAddress = ('localhost', 6666)
print "> Trying to connect to server on %s (port: %s)" % serverAddress
sock.connect(serverAddress)

# while True:
#     msg = raw_input("Input:")
for msg in ["hey", "how are you?", "i'm ok.\n"]:
    if msg:
        sock.sendall(msg)
    else:
        break

while True:
    msg = sock.recv(BUFSIZE)
    
    if not msg: break

    print "Received: %s" % msg

