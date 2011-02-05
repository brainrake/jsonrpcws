
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


Server
~~~~~~

To create a service, subclass ``JSONRPCWebSocket`` and decorate it with 
``@eventlet.websocket.WebSocketWSGI``.

Any methods defined on the subclass, whose names don't start
with an underscore (_) will be callable methods in the service.

The id of the current request is available through ``self._id`` .

You can override the event handlers ``_oninit()`` and ``_onclose()`` .

The Eventlet WebSocket object is available through ``self._ws`` .

Example: ::

    @eventlet.websocket.WebSocketWSGI
    class MyService(jsonrpcws.JsonRpcWebSocket):
        def hello(name):
            print "got hello from", name
            if self._id: # if this is a request, return a (response, error) tuple
                return ( ["hi, "+name], None)
        def _oninit():
            print self._ws.environ

To run it ::

    eventlet.wsgi.server(eventlet.listen(('', 8888)), MyService)


Client
~~~~~~

This section is under development.
