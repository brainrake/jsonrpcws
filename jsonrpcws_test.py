#!/usr/bin/env python
import jsonrpcws
import eventlet

@eventlet.websocket.WebSocketWSGI
class MyService(jsonrpcws.JsonRpcWsService):
    clients = set()

    def onopen(self):
        self.clients.add(self)
        self.username=""
    
    def onclose(self, error):
        self.clients.remove(self)
        for c in self.clients:
            c.notify("joinpart",[])

    class local:
        def clients(service):
            return ( [c.username for c in service.clients], None)
            
        def say(service, message):
            for c in service.clients:
                #c.remote.message(service.username, message)
                c.notify("message", [service.username, message])
                
        def set_username(service, username):
            service.username = username
            for c in service.clients:
                c.notify('joinpart',[])
                

eventlet.wsgi.server(eventlet.listen(('', 8888)), MyService)
