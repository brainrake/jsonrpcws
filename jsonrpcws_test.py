#!/usr/bin/env python
import jsonrpcws
import eventlet

@eventlet.websocket.WebSocketWSGI
class MyService(jsonrpcws.JsonRpcWebSocket):
    _clients = set()
    
    def clients(self):
        return ( [c._username for c in self._clients], None)
        
    def say(self, message):
        for c in self._clients:
            c._notify("message", [self._username, message])
            
    def set_username(self, username):
        self._username = username
        for c in self._clients:
            c._notify("joinpart",[])
            
    def _onopen(self):
        self._clients.add(self)
        self._username=""

    def _onclose(self):
        self._clients.remove(self)
        for c in self._clients:
            c._notify("joinpart",[])

eventlet.wsgi.server(eventlet.listen(('', 8888)), MyService)
