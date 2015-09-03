#!/usr/bin/env python
import socket as sk
import select as sl
import logging

#---------------------------------------------------------------------#
# TO-DO
# 1. Implement logging - do this early
# 2. Add some command line options - debug! or logging level?

#---------------------------------------------------------------------#

class AceServer(object):
    def __init__(self, debug = False):
        print "Creating AceServer instance..."
        self._debug = debug
        self._BUFSIZE = 4096


    def startListening(self):

        listenerSock = sk.socket(sk.AF_INET, sk.SOCK_STREAM) # would make a member, but eventually will be async...
        serverAddress = ('localhost', 6666) # rad port number, eh?
        if self._debug: print "> Starting server on %s (port: %s)" % serverAddress
        listenerSock.bind(serverAddress)

        # wait for a single connection (synchronous for now...)
        listenerSock.listen(1)

        # this is where it waits for a connection...
        while True:
            # ticker? ;-)
            if self._debug: print "> Waiting for a connection..."
            
            # get the connection, when it happens
            clientSock, clientAddress = listenerSock.accept()
            if self._debug: print clientSock, clientAddress

            msg = clientSock.recv(self._BUFSIZE)

            print msg

            
    def clientSession(self):
        transmission = []
        
        # note, in RL the amount sent and recv through the socket will be limited by the network buffer...
        # should consider this in the program somehow - make sure a single message is dealt with by enough 'recv's over the socket

        while True:
            clientInput = raw_input("")
            if clientInput:
                transmission.append(clientInput)
                # print repr(clientInput), len(clientInput)
            else:
                # currently an empty input ends transmission - should improve
                # UPDATE: apparently in RL a 0 bytes recv over a socket indicates the end of a session...
                self.echoTransmission(transmission)
                break

    def echoTransmission(self, trans = []):
        print "This transmission:\n"

        for t in trans:
            print "> %s" % t

        # or...
        # print "\n".join(trans)

        print "-" * 30
        print "End Transmission."

if __name__ == "__main__":

    server = AceServer(debug = True)
    server.startListening()