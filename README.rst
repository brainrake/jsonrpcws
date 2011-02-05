
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
