#!/usr/bin/env python
import socket as sk
import select as sl
import logging as lg
from sys import exit
from optparse import OptionParser

#---------------------------------------------#
# Written by Chris Lucas (4th September 2015) #
# lucasc896@gmail.com                         #
#                                             #
# Covering letter:  goo.gl/RlBRGF             #
# CV:               goo.gl/rmmKht             #
#---------------------------------------------#

class MessageBuf(object):
    """short container for messages to echo"""
    def __init__(self):
        self._msg = []
        self._echo = False

    def Add(self, string = ""):
        """populate the message"""
        # note: strip leading/trailing whitespace for neatness
        self._msg.append(string.strip())

    def EchoReady(self, choice = None):
        """dual-use function dealing with echo readiness"""
        if choice:
            self._echo = bool(choice)
        else:
            return self._echo

    def Get(self):
        """return the message"""
        return " ".join(self._msg)

    def Reset(self):
        """re-initialise"""
        self._msg = []
        self._echo = False

    def __str__(self):
        """string repr for easy debugging"""
        out = ""
        out += "MessageBuf Container:: "
        out += " msg: " + " ".join(self._msg)
        out += " echo: " + str(self._echo)
        return out

#---------------------------------------------------------------------#

class AceyncServer(object):
    """an ace asynchronous echo server"""
    def __init__(self, debug = False):
        self.splash()
        self._debug = debug
        self._serverAddress = ('localhost', 6666)
        self._BUFSIZE = 4096
        self._MAXCLIENTS = 5
        self._socks = dict.fromkeys(['in', 'out', 'read', 'write', 'bad'], [])
        self._msgBuffers = {}

    def splash(self):
        w = 29
        print "\n", "="*w
        print "-      AceyncServer v0      -"
        print "-      by Chris Lucas       -"
        print "="*w, "\n"

    def run(self):
        """main workhorse function"""

        # create main listener socket (IP, streaming)
        self._serverSock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

        lg.info("Starting server on %s (port: %s)" % self._serverAddress)

        try:
            self._serverSock.bind(self._serverAddress)
        except Exception, e:
            lg.error("ERROR binding server socket with %s. Exception: %s" % (self._serverAddress, e))
            exit()

        # make it non-blocking!
        self._serverSock.setblocking(0)

        # set it to listen
        self._serverSock.listen(self._MAXCLIENTS)

        self._socks['in'].append(self._serverSock)

        
        # as long as there are any input sockets, it runs
        while len(self._socks['in']) > 0:
            # self.printSockLists('Beginning of loop.')

            # use select to update all ready sockets, and check for dodgy socks
            timeout = 20 # add timeout to keep the server appearing as working
            self._socks['read'], self._socks['write'], self._socks['bad'] = sl.select(self._socks['in'],
                                                                                    self._socks['out'],
                                                                                    self._socks['in'],
                                                                                    timeout)

            if not (self._socks['read'] or self._socks['write'] or self._socks['bad']):
                lg.info("Timed out.")

            # check if there are ever any socks in error
            for bSock in self._socks['bad']:
                lg.warning("BAD SOCK: %s" % bSock)
                self._socks['in'].remove(bSock)
                if bSock in self._socks['out']:
                    self._socks['out'].remove(bSock)
                del self._msgBuffers[bSock]
                bSock.close()


            # loop through all readable socks
            for rSock in self._socks['read']:
                lg.debug("Read loop: %s" % rSock)

                if rSock == self._serverSock:
                    # if the serverSock is ready to read, then accept the incoming client connection
                    newClientConn, newClientAddr = rSock.accept()
                    # make non-blocking too
                    newClientConn.setblocking(0)
                    
                    lg.info("New client connection: %s %s" % (newClientAddr, newClientConn))
                    
                    # add new socket to input list, ready for potential recv'ing
                    self._socks['in'].append(newClientConn)
                    
                    # add empty buffer entry
                    self._msgBuffers[newClientConn] = MessageBuf()

                    # if not already, add new socket to the output list, ready for potential send
                    if rSock not in self._socks['out']:
                        self._socks['out'].append(newClientConn)
                else:
                    # if readable socket is one of the clients, then recv
                    recvMsg = rSock.recv(self._BUFSIZE)

                    if recvMsg:
                        # if message received, then add to message buffer
                        lg.info("Message received from %s: %s" % (rSock.getpeername(),
                                                                    recvMsg.rstrip("\n")))
                        # note: don't rstrip the '\n' from the buffered message!
                        self._msgBuffers[rSock].Add(recvMsg)

                        # check if message is ready to be echoed
                        if recvMsg[-1] == "\n":
                            lg.debug("End of line received. Will echo.")
                            self._msgBuffers[rSock].EchoReady(True)
                    else:
                        # if no message received, the client must be gone, so remove
                        lg.debug("Removing disconnected client: %s" % rSock)
                        self._socks['in'].remove(rSock)
                        if rSock in self._socks['out']:
                            self._socks['out'].remove(rSock)
                        del self._msgBuffers[rSock]
                        rSock.close()


            for wSock in self._socks['write']:
                lg.debug("Write loop: %s" % wSock)

                # check whether there's a message ready to be echoed
                if self._msgBuffers[wSock].EchoReady(): 
                    self.echoBack(wSock, self._msgBuffers[wSock].Get())
                    self._msgBuffers[wSock].Reset() # reset message buffer, ready for another

    def echoBack(self, sock, msg = ""):
        """echo wrapper function"""
        lg.info("Echoing to %s: %s" % (sock.getpeername(), msg))
        # note: using 'sendall' lets python deal with packet splitting according to network buffer
        sock.sendall(msg)

    def printSockLists(self, label = ""):
        """useful for debugging"""
        print "-"*40
        print label, "\n"
        for key in self._socks:
            print " %s:\t" % key, self._socks[key]
        print "-"*40

#---------------------------------------------------------------------#
#---------------------------------------------------------------------#

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="run server in Debug mode")
    parser.add_option('--log', help = 'Set logging level (WARNING/DEBUG/INFO/ERROR/CRITICAL)',
                        dest = 'loglevel', default = 'INFO')
    (opts, args) = parser.parse_args()

    if opts.debug:
        opts.loglevel = 'DEBUG'

    lg.basicConfig(level=opts.loglevel.upper())

    # create instance of server and start in running
    server = AceyncServer(debug = opts.debug)
    server.run()
