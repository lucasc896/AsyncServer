Some kind of rough outline of what should be happening

_SERVER_

`While True:
    Listen for new client
        if client:
            create SOCKET
            SOCKET.SETBLOCKING(0) - non-blocking - send this to the CLIENT OBJECT
            create a CLIENT instance
            continue listening`

Note: set a maximum number of clients (e.g. `serversocket.listen(5)`)
Uses server sockets ('socket' python module)

_CLIENT_
`While True:
    'Tell me something cool'
    SOCKET.RECV
    - implement a timeout! (60 secs?)
    store line by line
    if transmission end:
        SOCKET.SEND
        echo back what you told me`
    SOCKET.SHUTDOWN(1) - may not need this with 'python socket'
    SOCKET.CLOSE()