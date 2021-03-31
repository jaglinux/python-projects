import turtle

window = turtle.Screen()
window.title('Pong - by Jag')
window.bgcolor('blue')
# width 800 height 600
window.setup(800, 600)
# use update() to update the window
window.tracer(0)

class turtle_factory:
    def __init__(self, x, y, dx=None, dy=None):
        self.t = turtle.Turtle()
        self.t.speed(0)
        self.t.color('white')
        self.t.shape('square')
        # no drawing
        self.t.penup()
        self.t.goto(x, y)
        self.dx = dx
        self.dy = dy

    def resize(self, x, y):
        return self.t.shapesize(x, y)

    def pos(self):
        return self.t.position()

    def moveX(self, x=None):
        _x = None
        if x:
            _x = x
        else:
            _x = self.dx
        self.t.setx(self.pos()[0] + _x)

    def moveY(self, y=None):
        _y = None
        if y:
            _y = y
        else:
            _y = self.dy
        self.t.sety(self.pos()[1] + _y)

Bat_A = turtle_factory(-350, 0)
Bat_A.resize(5, 1)
Bat_B = turtle_factory(350, 0)
Bat_B.resize(5, 1)
Ball = turtle_factory(0, 0, 0.2, 0.2)

print('Initial Bat_A pos is ', Bat_A.pos(), ' size is ', Bat_A.resize(None, None))
print('Initial Bat_B pos is ', Bat_B.pos(), ' size is ', Bat_B.resize(None, None))
print('Initial Ball pos is ', Ball.pos(), ' size is ', Ball.resize(None, None))

while True:
    window.update()
    Ball.moveX()
    Ball.moveY()
    if Ball.pos()[1] > 290:
        Ball.t.sety(290)
        Ball.dy *= -1
    elif Ball.pos()[1] < -290:
        Ball.t.sety(-290)
        Ball.dy *= -1
    if Ball.pos()[0] > 350:
        Ball.t.goto(0,0)
        Ball.dx *= -1
    if Ball.pos()[0] < -350:
        Ball.t.goto(0,0)
        Ball.dx *= -1
