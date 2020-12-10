var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var kafka = require('kafka-node');
var port = 8081;

var Consumer = kafka.Consumer,
 client = new kafka.KafkaClient("localhost:9092"),
 consumer = new Consumer(
 client, [ { topic: 'processedtweets2', partition: 0 } ], { autoCommit: false });

app.get('/tst', function(req, res){
    res.sendfile('index.html');
});

consumer = consumer.on('message', function(message) {
    io.emit("message", message.value);
});

http.listen(port, function(){
    console.log("Running on port " + port)
});