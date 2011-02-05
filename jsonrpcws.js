/*
jsonrpcws.js
JSON-RPC over Websocket client implementation
@author: Martin Boros <brainrape@chaosmedia.hu>

usage:

var service = {
    hello: function(id, name){
        alert("Got hello from "+name)
        if(id){ //if this is a request, return [result, error]
            return ['hi, '+name]
        }
    }
    _onopen: function(){
        this.hello("Alice")
        this._request(1,"hello",["Alice"])
    }
}

jsonrpcws("ws://localhost:8888/",service)

*/


//TODO: convert to class
function jsonrpcws(url, service){
    if(!window.console){window.console={log:function(){}}}
    if(!window.WebSocket){throw "jsonrpcws error: WebSockets not available"}
    if(!window.JSON){throw "jsonrpcws error: JSON (de)serializer not available"}

    CALLBACK_QUEUE_SIZE = 32
    service._id = null
    service.__counter = 1
    service.__callbacks = []
    
    service._request = function(method, params, callback, id){
        /// Send a request
        if(id===undefined){ id = service.__counter; service.__counter += 1; }
        message = JSON.stringify({id:id, method:method, params:params})
        console.log("Websocket at "+url+" sending message: "+message)
        service.ws.send(message)
        if(callback){
            service.__callbacks = [[id, callback]].concat(service.__callbacks)
        }
        if(service.__callbacks.length > CALLBACK_QUEUE_SIZE){
            service.__callbacks.pop()
        }
    }

    service._notify = function(method, params){
        /// Send a notification
        this._request (method, params, null, null)
    }

    service._response = function(id, result, error){
        /// Send a response
        message = JSON.stringify({id:id, result:result, error:error})
        console.log("Websocket at "+url+" sending message: "+message)
        service.ws.send(message)
    }

    service._close = function(){
        /// Close the connection
        service.ws.close()
    }
    
    // Set up WebSocket and event handlers
    service.ws = new WebSocket(url);

    service.ws.onopen = function(){
        console.log("Websocket at "+url+" connection open.")
        if(service['_onopen']){ service._onopen.apply(service) }
    }

    service.ws.onmessage = function(evt) {
        //TODO: error checking
        data = JSON.parse(evt.data);
        console.log("Websocket at "+url+" got data: ", evt.data);
        if (data['method']){
            service_method = service[data['method']]
            service._id = data['id']
            ret = service_method.apply(service, data['params'])
            service._id = null
            if(data['id']){
                service._response(data['id'], ret[0], ret[1])
            }
        } else if (data['result']){
            for(var i=0;i<service.__callbacks.length;i++){
                if(service.__callbacks[i][0] == data['id']){
                    service.__callbacks[i][1].apply(service, [data['result'], data['error']])
                    service.__callbacks.splice(i,1)
                    break;
                }
            }
        } else {
            console.log("Websocket at "+url+" error.");
        }
    };

    service.ws.onerror = function(){
        console.log("Websocket at "+url+" error.");
    }

    service.ws.onclose = function(){
        console.log("Websocket at "+url+" connection closed.")
        if(service['_onclose']){ service._onclose.apply(service) }
    }
}

