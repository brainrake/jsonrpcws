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
#     def hello(id, name):
#         print "got hello from", name
#         if id: # if this is a request, return a (response, error) tuple
#             return ( ["hi, "+name], None)


#TODO: error handling

from eventlet import websocket
import simplejson

class JsonRpcWebsocket():
    def __init__(self,ws):
        # Websocket handler.
        self.ws = ws
        self._onopen()
        while 1:
            print 'wait'
            ws_message = ws.wait()
            print 'ws_message', ws_message
            if ws_message is None:
                break;
            message = simplejson.loads(ws_message)
            print message
            if message.get('method',None):
                self.__onrequest(message.get("id",None),
                                 message["method"],
                                 message.get("params",[]))
            elif message.get('result'):
                self.__onresult(message["id"],
                                message["result"],
                                message.get("error",None))
            else:
                break; #JSON-RPC error. Close connection.
        self._onclose()
        
    def _request(self, id, method, params):
        '''Send JSON-RPC request or notification'''
        message = simplejson.dumps({'id':id, 'method':method, 'params':params})
        self.ws.send( message )

    def _response(self, id, result, error=None):
        '''Send JSON-RPC response'''
        message = simplejson.dumps({'id':id, 'result':result, 'error':error})
        self.ws.send(message)

    def _onopen():
        '''Socket open event handler.'''
        return

    def _onclose():
        '''Socket close event handler.'''
        return

    def __onrequest(self, id, method, params):
        # Request event handler. Invokes `method` on the class instance
        # TODO: check for _
        service_method = getattr(self, method)
        if id:
            result, error = service_method(id, *params)
            self._response(id, result, error)
        else :
            service_method(id, *params)
        
    def __onresponse(self, id, result, error):
        # Response event handler.
        raise NotImplementedError
