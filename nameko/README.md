docker run --rm -it --hostname my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management <br/>
http://localhost:15672 <br/>

nameko run helloworld <br/>

# On Another Terminal
nameko shell <br/>

  n.rpc.greeting_service.hello("world0") <br/>
