#!/usr/bin/env python
import socket as sk
from sys import argv

if len(argv) > 1:
    msg = argv[1]
else:
    msg = "Hey Mum!"

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
serverAddress = ('localhost', 6666)
print "> Trying to connect to server on %s (port: %s)" % serverAddress
sock.connect(serverAddress)

sock.sendall(msg)