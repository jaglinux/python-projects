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
Ball = turtle_factory(0, 0, 0.5, 0.5)
Score = turtle_factory(0, 260)
Score.t.hideturtle()
score_a = 0
score_b = 0
Score.t.write(f'Player A:{score_a}  Player B:{score_b}', align='center', font=('Ariel', 24, 'normal'))
print('Initial Bat_A pos is ', Bat_A.pos(), ' size is ', Bat_A.resize(None, None))
print('Initial Bat_B pos is ', Bat_B.pos(), ' size is ', Bat_B.resize(None, None))
print('Initial Ball pos is ', Ball.pos(), ' size is ', Ball.resize(None, None))


def bat_a_up():
    Bat_A.moveY(20)


def bat_a_down():
    Bat_A.moveY(-20)


def bat_b_up():
    Bat_B.moveY(20)


def bat_b_down():
    Bat_B.moveY(-20)


window.listen()
window.onkeypress(bat_a_up, key='w')
window.onkeypress(bat_a_down, key='s')
window.onkeypress(bat_b_up, key='Up')
window.onkeypress(bat_b_down, key='Down')

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
        Ball.t.goto(0, 0)
        Ball.dx *= -1
        score_a += 1
        Score.t.clear()
        Score.t.write(f'Player A:{score_a}  Player B:{score_b}', align='center', font=('Ariel', 24, 'normal'))
    elif Ball.pos()[0] < -350:
        Ball.t.goto(0, 0)
        Ball.dx *= -1
        score_b += 1
        Score.t.clear()
        Score.t.write(f'Player A:{score_a}  Player B:{score_b}', align='center', font=('Ariel', 24, 'normal'))
    # collision
    if Ball.pos()[0] < -340 and Ball.pos()[1] < Bat_B.pos()[1] + 50 and Ball.pos()[1] > Bat_B.pos()[1] - 50:
        Ball.dx *= -1
    elif Ball.pos()[0] > 340 and Ball.pos()[1] < Bat_B.pos()[1] + 50 and Ball.pos()[1] > Bat_B.pos()[1] - 50:
        Ball.dx *= -1
