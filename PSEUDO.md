Some kind of rough outline of what should be happening

_SERVER_

`While True:
    Listen for new client
        if client:
            create a CLIENT instance
            continue listening`

Note: set a maximum number of clients (e.g. `serversocket.listen(5)`)
Uses server sockets ('socket' python module)

_CLIENT_
`While True:
    'Tell me something cool'
    store line by line
    if transmission end:
        echo back what you told me`