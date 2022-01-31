from nameko.rpc import rpc
import time

class GreetingService:
    name = "greeting_service"

    @rpc
    def hello(self, name):
        time.sleep(25)
        return "Hello, {}!".format(name)
