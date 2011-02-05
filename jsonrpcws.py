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
# class MyService(jsonrpcws.JsonRpcWebsocket):
#     def hello(name):
#         print "got hello from", name
#         if self._id: # if this is a request, return a (response, error) tuple
#             return ( ["hi, "+name], None)


#TODO: error handling

from eventlet import websocket
import simplejson


class JsonRpcError(Exception):
    pass

class JsonRpcWebSocket(object):
    CALLBACK_QUEUE_SIZE = 32
    
    def __init__(self,ws):
        # Websocket handler.
        self._ws = ws
        self._id = None
        self.__counter = 1
        self.__callbacks = []
        
        self._onopen()
        try:
            while 1:
                ws_message = ws.wait()
                #print 'ws_message', ws_message
                if ws_message is None: break;
                try:
                    message = simplejson.loads(ws_message)
                except Exception:
                    raise JsonRpcError("error decoding json")
                #print message
                if message.get('method',None):
                    self.__onrequest(message.get("id",None),
                                     message["method"],
                                     message.get("params",[]))
                elif message.get('result'):
                    self.__onresponse(message["id"],
                                      message["result"],
                                      message.get("error",None))
                else:
                    raise JsonRpcError("could not find 'method' or 'result' in message")
        except JsonRpcError, e:
            self._onerror(e)
            raise
        self._onclose()

    def _request(self, method, params, id=None, callback=None):
        '''Send JSON-RPC request. Callback will run when response arrives.'''
        if not id: #TODO:fix this
            id = self.__counter
            self.__counter += 1
        message = simplejson.dumps({'id':id, 'method':method, 'params':params})
        self._ws.send( message )
        
        if callback:
            self.__callbacks.insert(0,(id,callback))
            if len(self.__callbacks) > CALLBACK_QUEUE_SIZE:
                self.__callbacks.pop()
        return

    def _notify(self, method, params):
        '''Send JSON-RPC notification'''
        message = simplejson.dumps({'id':None, 'method':method, 'params':params})
        self._ws.send( message )

    def _response(self, id, result, error=None):
        '''Send JSON-RPC response'''
        message = simplejson.dumps({'id':id, 'result':result, 'error':error})
        self._ws.send(message)
        
    def _onopen():
        '''Socket open event handler.'''
        return

    def _onclose():
        '''Socket close event handler.'''
        return

    def _onerror(e):
        '''Error handler.'''
        print "JSON-RPC error: ",e
        return

    def __onrequest(self, id, method, params):
        # Request event handler. Invokes `method` on the class instance
        if method[0] == '_': raise JsonRpcError("method names cannot start with _")
        service_method = getattr(self, method)
        self._id = id
        ret = service_method(*params)
        self._id = None
        if id:
            result, error = ret
            self._response(id, result, error)
        
    def __onresponse(self, id, result, error):
        # Response event handler.
        for c in self.__callbacks:
            if c[0]==id:
                c[1](result, error)
                self.__callbacks.remove(c)
