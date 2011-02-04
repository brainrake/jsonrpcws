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
    },
    _onopen: function(ws){
        service._request(1,"hello",["Alice"])
    }
}

jsonrpcws("ws://localhost:8888/",service)

*/



function jsonrpcws(url, service){
    //TODO: test if WebSockets are available
    //TODO: test if JSON is available
    
    service._request = function(id, method, params){
        message = JSON.stringify({id:id, method:method, params:params})
        service.ws.send(message)
    }

    service._response = function(id, result, error){
        message = JSON.stringify({id:id, result:result, error:error})
        service.ws.send(message)
    }

    service._close = function(){
        service.ws.close()
    }
    
    service.ws = new WebSocket(url);

    service.ws.onopen = function(){
        console.log("Websocket connection open to "+url)
        if(service['_onopen']){ service._onopen.apply(service) }
    }

    service.ws.onmessage = function(evt) {
        //TODO: error checking
        data = JSON.parse(evt.data);
        console.log("Websocket to "+url+" got data:", evt.data);
        if (data['method']){
            service_method = service[data['method']]
            ret = service_method.apply(service, [data['id']].concat(data['params']))
            if(data['id']){
                _response(data['id'], ret[0], ret[1])
            }
        }
    };

    service.ws.onerror = function(){
        console.log("Websocket error.")
    }

    service.ws.onclose = function(){
        console.log("Websocket connection closed to "+url)
        if(service['_onclose']){ service._onclose.apply(service) }
    }
}


$(function(){
    try {
    }
    catch (err) {
        console.log(err);
    }
})


