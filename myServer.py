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
        self._MAXCLIENTS = 5
        self._socks = dict.fromkeys(['in', 'out', 'read', 'write', 'bad'], [])
        self._msgBuffers = {}

    def startListening(self):
        """main workhorse function"""

        # create main listener socket
        self._serverSock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

        if self._debug:
            print "> Starting server on %s (port: %s)" % self._serverAddress
        self._serverSock.bind(self._serverAddress)

        # make it non-blocking!
        self._serverSock.setblocking(0)

        # set it to listen
        self._serverSock.listen(self._MAXCLIENTS)

        self._socks['in'].append(self._serverSock)

        
        # as long as there are any input sockets, it runs
        while len(self._socks['in']) > 0:

            # use select to update all ready sockets, and check for dodgy socks
            self._socks['read'], self._socks['write'], self._socks['bad'] = sl.select(self._socks['in'],
                                                                                    self._socks['out'],
                                                                                    self._socks['in'])

            if self._debug: self.printSockLists("Start of loop")
            if self._debug: print self._msgBuffers

            # check if there are ever any socks in error
            for bSock in self._socks['bad']:
                print "BAD SOCK:", bSock
                if bSock == self._serverSock:
                    raise "Bad Server Sock!"
                # if any sock is in error or has an exception, remove entirely
                self._socks['in'].remove(bSock)
                if bSock in self._socks['out']:
                    self._socks['out'].remove(bSock)
                bSock.close()


            # loop through all readable socks
            for rSock in self._socks['read']:

                if rSock == self._serverSock:
                    # if the serverSock is ready to read, then accept the
                    # incoming client connection
                    newClientConn, newClientAddr = rSock.accept()
                    # make non-blocking too
                    newClientConn.setblocking(0)
                    
                    if self._debug:
                        print "> New client connection: %s %s" % (newClientAddr, newClientConn)
                    
                    # add new socket to input list, ready for potential recv'ing
                    self._socks['in'].append(newClientConn)
                    
                    # add empty buffer entry
                    self._msgBuffers[newClientConn] = []

                    # if not already, add new socket to the output list, ready for potential send
                    if rSock not in self._socks['out']:
                        self._socks['out'].append(newClientConn)
                else:
                    # if readable socket is one of the clients, then recv
                    recvMsg = rSock.recv(self._BUFSIZE)
                    
                    if recvMsg:
                        # if message received, then add to buffers to echo later
                        print "Message received from %s: %s" % (rSock.getpeername(), recvMsg)
                        self._msgBuffers[rSock].append(recvMsg)
                    else:
                        # if no message received, the client must be gone, so remove
                        self._socks['in'].remove(rSock)
                        if rSock in self._socks['out']:
                            self._socks['out'].remove(rSock)
                        rSock.close()

            for wSock in self._socks['write']:
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
        # note: using 'sendall' lets python deal with packet splitting according
        # to network buffer
        sock.sendall(msg)

    def printSockLists(self, label = ""):
        """useful for debugging"""
        print "-"*40
        print label, "\n"
        print "  InputSocks:", self._socks['in']
        print "  OutputSocks:", self._socks['out']
        print "  ReadableSocks:", self._socks['read']
        print "  WritableSocks:", self._socks['write']
        print "  BadSocks:", self._socks['bad']
        print "-"*40

if __name__ == "__main__":

    server = AceyncServer(debug = False)
    server.startListening()