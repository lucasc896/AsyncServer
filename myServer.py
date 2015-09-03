#!/usr/bin/env python
import socket as sk
import select as sl

#---------------------------------------------------------------------#
# TO-DO
# 1. Implement logging - do this early

#---------------------------------------------------------------------#


class AceServer(object):
    def __init__(self, debug = False):
        print "Creating AceServer instance..."
        self._debug = debug


    def startListening(self):
        
        # make this a cool ticking thing
        print "Listening..."

        # this is where it waits for a connection...
        # for now, just assume it gets one straight away
        newClient = True
        if newClient:
            self.session()

    def clientSession(self):
        transmission = 
        while True:
            clientInput = raw_input("")
            if clientInput:
                transmission.append(clientInput)
                # print repr(clientInput), len(clientInput)
            else:
                # currently an empty input ends transmission - should improve
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

    server = AceServer()
    server.startListening()