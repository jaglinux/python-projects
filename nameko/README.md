# 1. First Terminal
mkdir nameko && cd nameko <br/>
python3 -m venv env <br/>
source env/bin/activate <br/>
docker run --rm -it --hostname my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management <br/>
http://localhost:15672 <br/>

nameko run helloworld <br/>

# 2. On Another Terminal
source env/bin/activate <br/>
nameko shell <br/>

  n.rpc.greeting_service.hello("world0") <br/>

Repeat the step 2 on multiple Terminals to produce n number of messages consumed by n number consumers of nameko microservice <br/>

At the end, in all terminals, <br/> 
deactivate <br/>
