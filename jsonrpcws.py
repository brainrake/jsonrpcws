#!/usr/bin/env python
#
# jsonrpcws.py
# 
# JSON-RPC 1.0 over Websocket server implementation
# @author: Martin Boros <brainrape@chaosmedia.hu>
#
# usage:
#
# import eventlet
# @eventlet.websocket.WebSocketWSGI
# class MyService(jsonrpcws.JsonRpcWebSocket):
#     def hello(self, name):
#         print "got hello from", name
#         if self._id: # if this is a request, return a (response, error) tuple
#             return ( ["hi, "+name], None)


#TODO: error handling
#TODO: doc
#TODO: licence

from eventlet import websocket
import simplejson


class JsonRpcError(Exception):
    pass

class JSONRPCWSService(object):
    _CALLBACK_QUEUE_SIZE = 32
    
    def __init__(self, ws):
        # Websocket handler.
        self.ws = ws
        self._id = None
        self._next_id = 1
        self._callbacks = []
        
        self.onopen()
        try:
            while 1:
                ws_message = ws.wait()
                if ws_message is None: break;
                try:
                    message = simplejson.loads(ws_message)
                except Exception:
                    raise JsonRpcError("error decoding json")
                if message.get('method',None):
                    self._onrequest(message.get("id",None),
                                    message["method"],
                                    message.get("params",[]))
                elif message.get('result'):
                    self._onresponse(message["id"],
                                     message["result"],
                                     message.get("error",None))
                else:
                    raise JsonRpcError("malformed message received")
        except JsonRpcError, e:
            self.onclose(e)
        else:
            self.onclose(None)

    def request(self, method, params, callback=None):
        '''Send JSON-RPC request. Callback will run when response arrives.'''
        id = None
        if callback:
            id = self._next_id
            self._next_id += 1
        message = simplejson.dumps({'id':id, 'method':method, 'params':params})
        self._ws.send( message )
        
        if callback:
            if len(self._callbacks) > _CALLBACK_QUEUE_SIZE:
                self._callbacks.pop()
            self._callbacks.insert(0,(id,callback))

    def notify(self, method, params):
        '''Send JSON-RPC notification'''
        message = simplejson.dumps({'id':None, 'method':method, 'params':params})
        self.ws.send( message )

    def respond(self, id, result, error=None):
        '''Send JSON-RPC response'''
        message = simplejson.dumps({'id':id, 'result':result, 'error':error})
        self.ws.send(message)
        
    def onopen():
        '''Socket open event handler.'''
        return

    def onclose(error):
        '''Socket close event handler.'''
        return

    def _onrequest(self, id, method, params):
        # Request event handler. Invokes `method` on the class instance
        if method[0] == '_': raise JsonRpcError("method names cannot start with _")
        # Get the method, bound to the service instance
        service_method = getattr(self.local, method).__get__(self)
        self._id = id
        ret = service_method(*params)
        self._id = None
        if id:
            result, error = ret
            self.respond(id, result, error)
        
    def _onresponse(self, id, result, error):
        # Response event handler.
        for c in self._callbacks:
            if c[0]==id:
                c[1](result, error)
                self._callbacks.remove(c)
