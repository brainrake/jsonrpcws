#!/usr/bin/env python
import jsonrpcws
import eventlet

@eventlet.websocket.WebSocketWSGI
class MyService(jsonrpcws.JsonRpcWebsocket):
    def hello(self, id, name):
        print "got hello from", name
        if id:
            return ( ["hi, "+name], None)
    def _onopen(self):
        print 'open'
        self._request(0,'hello',['Bob'])
        return
    def _onclose(self):
        print 'close'
        return

eventlet.wsgi.server(eventlet.listen(('', 8888)), MyService)

