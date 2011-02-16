
JSON-RPC over WebSockets
========================


This is an implementation of
`JSON-RPC 1.0
<http://json-rpc.org/wiki/specification>`_
over `WebSockets
<http://dev.w3.org/html5/websockets/>`_.

The server is implemented in Python, using the `Eventlet
<http://eventlet.net/>`_
networking library.

The client is ECMAScript (JavaScript), and runs in the
latest browsers supporting WebSockets.


Project Status
--------------

The project is in **alpha** state.
It is functionally complete, but is yet to be tested extensively.
I will use it in production soon, so expect improvements.


Usage
-----

The server needs the ``Eventlet`` python networking library.
to install it on debian-based systems, do
``sudo apt-get install python-eventlet``.


Server
~~~~~~

To create a service, subclass ``JSONRPCWebSocket`` and decorate it with 
``@eventlet.websocket.WebSocketWSGI``.

Any methods defined in the inner class `local` can be called remotely.
They receive the service instance as the first argument.

You can override the event handlers ``oninit()`` and ``onclose()`` for
additional functionality.

The id of the current request is available through ``service._id`` .
If this value is not ``None``, the method has to return a
``(result, error)`` tuple.

The Eventlet WebSocket object is available through ``service.ws`` .

To send messages, use ``notify(self, method, params)`` and 
``request(self, method, params, callback=None)``.
The callback gets two arguments: ``result`` and ``error``.
To explicitly send a response, use ``respond(self, id, result, error)``.

You can also ``close()`` the socket.

Example: ::

    @eventlet.websocket.WebSocketWSGI
    class MyService(jsonrpcws.JSONRPCWSService):
        class local: # the methods in this class can be called remotely
            def hello(service, name):
                print "got hello from", name
                if self._id: # if this is a request, not a notification
                    return ( ["hi, "+name], None) # return a (response, error) tuple
        def oninit(self):
            print self.ws.environ
            self.nofify("hi",["the server"])

To run it, pass the class (not an instance) to ``eventlet.wsgi.server``.
A new instance will be created for every incoming WebSocket connection. ::

    eventlet.wsgi.server(eventlet.listen(('', 8888)), MyService)


Client
~~~~~~

To create a service, instantiate JSONRPCWSService. The client API is
almost identical to the server. Methods defined in the ``local``
object will be remotely callable. The service instance is available
through ``this``.

``notify``, ``request``, ``respond``, ``close``, ``oninit`` and
``onclose`` are similarly available.

The WebSocket instance is available through ``this.ws`` .


Example: ::

    var service_def = {
        local:{
            hi: function(who){
                alert("got hi from "+who)
            }
        },
        onopen: function(){
            this.notify("hello", ["the client"])
        }
    }
    var service = new JSONRPCWSService("ws://localhost:8888/",service_def)

