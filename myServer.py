#!/usr/bin/env python
import socket as sk
import select as sl
import logging
# import errno
# from time import sleep

#---------------------------------------------------------------------#
# TO-DO
# 1. Implement logging - do this early
# 2. Add some command line options - debug! or logging level?

#---------------------------------------------------------------------#

class AceyncServer(object):
    """an asynchronous echo server"""
    def __init__(self, debug = False):
        print "\nCreating AceyncServer instance...\n"
        self._debug = debug
        self._serverAddress = ('localhost', 6666)
        self._BUFSIZE = 4096
        self._inputSocks = []
        self._outputSocks = []
        self._goodReadSocks = []
        self._goodWriteSocks = []
        self._badSocks = []
        self._msgBuffers = {}

    def startListening(self):
        """main workhorse function"""

        self._serverSock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        if self._debug: print "> Starting server on %s (port: %s)" % self._serverAddress
        self._serverSock.bind(self._serverAddress)

        # make it non-blocking!
        self._serverSock.setblocking(0)

        self._serverSock.listen(5)

        self._inputSocks.append(self._serverSock)

        
        # as long as there are any input sockets, it runs
        while len(self._inputSocks) > 0:

            # use select to update all ready sockets, and check for dodgy error socks
            self._goodReadSocks, self._goodWriteSocks, self._badSocks = sl.select(self._inputSocks, self._outputSocks, self._inputSocks)

            if self._debug: self.printSockLists("Start of loop")
            if self._debug: print self._msgBuffers

            # check if there are ever any socks in error
            for bSock in self._badSocks:
                print "BAD SOCK:", bSock
                if bSock == self._serverSock:
                    raise "Bad Server Sock!"
                # if any sock is in error or has an exception, remove it entirely
                self._inputSocks.remove(bSock)
                if bSock in self._outputSocks:
                    self._outputSocks.remove(bSock)
                bSock.close()


            # loop through all readable socks
            for rSock in self._goodReadSocks:

                if rSock == self._serverSock:
                    # if the serverSock is readable, then accept the incoming client connection
                    newClientConn, newClientAddr = rSock.accept()
                    
                    # make non-blocking too
                    newClientConn.setblocking(0)
                    
                    if self._debug: print "> New client connection:", newClientAddr, newClientConn
                    # add new socket to input list, ready for potential recv'ing
                    self._inputSocks.append(newClientConn)
                    
                    # add empty buffer entry
                    self._msgBuffers[newClientConn] = []

                    # if not already, add new socket to the output list, ready for potential send'ing
                    if rSock not in self._outputSocks:
                        self._outputSocks.append(newClientConn)
                else:
                    # if readable sock is one of the clients, then recv from it
                    recvMsg = rSock.recv(self._BUFSIZE)
                    
                    if recvMsg:
                        # if message received, then add to buffers to echo later
                        print "Message received from %s: %s" % (rSock.getpeername(), recvMsg)
                        self._msgBuffers[rSock].append(recvMsg)
                    else:
                        # if no message received, the client must be gone, so remove
                        self._inputSocks.remove(rSock)
                        if rSock in self._outputSocks:
                            self._outputSocks.remove(rSock)
                        rSock.close()

            for wSock in self._goodWriteSocks:
                if self._debug: print "Write loop:", wSock
                if self._debug: print self._msgBuffers

                # check whether there's a buffered message for this sock
                try:
                    echoMsg = " ".join(self._msgBuffers[wSock])
                except KeyError:
                    if self._debug: print "> No msg to echo back..."
                    echoMsg = ""

                if echoMsg:
                    # if there is, send that bad boy back
                    self.echoBack(wSock, echoMsg)
                    self._msgBuffers[wSock] = []

            if self._debug: self.printSockLists("End of loop")

    def echoBack(self, sock, msg = ""):
        """echo wrapper function"""
        print "Echoing to %s: %s" % (sock.getpeername(), msg)
        sock.sendall(msg)

    def printSockLists(self, label = ""):
        """useful for debugging"""
        print "-"*40
        print label, "\n"
        print "  InputSocks:", self._inputSocks
        print "  OutputSocks:", self._outputSocks
        print "  ReadableSocks:", self._goodReadSocks
        print "  WritableSocks:", self._goodWriteSocks
        print "  BadSocks:", self._badSocks
        print "-"*40

if __name__ == "__main__":

    server = AceyncServer(debug = False)
    server.startListening()