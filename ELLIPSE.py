import pygame as pg
import sys, math
from random import random,randint

"""Программный код отрисовывает эллипс по заданным осям abcyx,ordin. При наведении на линию кривой
 эллипса отмеряются фокальные расстояния согласно математическим формулам. При наведении и удерживании 
 центрального зеленого кружка, можно смещать полюс схождения линий num_points деленных на 50. Для выхода из 
 программы нажать ESCAPE"""

RES = WIDTH, HEIGHT = 1600, 900
vec2 = pg.Vector2
CENTER = vec2(WIDTH // 2, HEIGHT // 2)
abcyx,ordin = 600,300
num_points = 900

class Coordinates:
    """Формирование и отрисовка осей координат"""
    def __init__(self,app):
        self.app = app.screen
        self.x,self.y = abcyx,ordin
        self.width = self.x + 50
        self.height = self.y + 50
    def draw(self):
        pg.draw.line(self.app, 'green',(CENTER[0], CENTER[1] + self.height),(CENTER[0],CENTER[1] - self.height),1)
        #
        pg.draw.line(self.app, 'red',(CENTER[0] - self.width, CENTER[1]),(CENTER[0] + self.width, CENTER[1]),1)

class Point:
    """Генерация точек"""
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.y = randint(-1, 1) * random() * self.b
        self.pos = self.get_points()

    def get_points(self):
        self.x = math.sqrt((pow(self.b, 2) - pow(self.y, 2)) * (pow(self.a, 2) / pow(self.b, 2)))
        return vec2(self.x, self.y)

class Object:
    """Отрисовка кривой эллипса"""
    def __init__(self,app):
        self.app = app.screen
        self.points = [Point(abcyx,ordin) for _ in range(num_points)]
        self.points.sort(key=lambda point: point.pos[1])
        #
        self.mouse = CENTER + vec2(0, 0)

    def get_color(self,y):
        c = 20 if y > CENTER[1] else -120
        return (80 + c // 2, 50, 200 + c)

    def draw(self):
        # Отрисовка линий расходящихся от центра
        [pg.draw.line(self.app,self.get_color(eLl[1]), self.mouse,eLl,3) for eLl in self.full_line[::num_points // 50]] #if ell.y < CENTER[1]
        #
        pg.draw.polygon(self.app, 'orange', self.full_line, 6)
        #
        pg.draw.circle(self.app, 'green', self.mouse, 15)

    def run(self):
        self.line = [point.get_points() for point in self.points]
        #
        linesPositive = [vec2(l[0],l[1]) + CENTER for l in self.line]
        linesNegative = [CENTER - vec2(l[0],l[1]) for l in self.line]
        self.full_line = linesPositive + linesNegative
        #
        self.draw()

    def control(self,event):
        pos = pg.mouse.get_pressed()
        if event.type == pg.KEYDOWN:
            sys.exit() if pg.K_ESCAPE else None
        if pos[0]: # Фиксация точки левой кнопкой
            self.mouse = pg.mouse.get_pos()
class Focus:
    """Отрисовка фокальных расстояний"""
    def __init__(self,app,obj):
        self.app = app.screen
        self.a, self.b = abcyx,ordin
        self.obj = obj

    def get_focus(self):
        c = math.sqrt(pow(self.a,2) - pow(self.b,2))
        return [vec2(c,0) + CENTER, vec2(-c,0) + CENTER]
    def draw_focuses(self):
        self.focuses = self.get_focus()
        [pg.draw.circle(self.app,'yellow',self.focuses[i],10) for i in range(2)]
        self.draw_lines()

    def draw_lines(self):
        self.mous = pg.mouse.get_pos()
        x,y = self.mous
        quality = (round(x,-1),round(y,-1)) #Округление координат точки
        set_direct = self.create_set()
        self.flag = False

        def line():
            return [self.get_focus()[0], (round(x, -1), round(y, -1)), self.get_focus()[1]]
        #
        if quality in set_direct: #Коллизия фокуса мышки и координат точек кривой
            self.flag = True
            [pg.draw.line(self.app,'cyan',line()[i],line()[i + 1],7) for i in range(2)]
            pg.draw.circle(self.app, 'lightgreen', self.mous, 12)

    def create_set(self):
        directory = set()
        for vec in self.obj.full_line:
            directory.add((round(vec[0],-1),round(vec[1],-1)))
        return directory
class Text:
    """Отрисовка текста"""
    def __init__(self,app,focus, x, y, num_focus):
        self.app = app
        self.focus = focus
        self.x,self.y = x,y
        self.number = num_focus
    def get_value(self):
        point = vec2(self.focus.get_focus()[self.number]) - CENTER
        mouse = vec2(pg.mouse.get_pos()) - CENTER
        res = point + mouse
        return round(math.sqrt(pow(res[0],2) + pow(res[1],2)),-1)
    def translate_value(self):
        self.get_value()
        if self.focus.flag:
            render = self.app.font.render(f'Фокус: {self.get_value()}',True,'red','grey')
        else: render = self.app.font.render(f'Фокус: {None}',True,'red','grey')
        #
        self.app.screen.blit(render,(self.x,self.y))

class App:
    def __init__(self):
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        pg.init()
        #
        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.ellipse = Object(self)
        self.coordinates = Coordinates(self)
        self.focus = Focus(self,self.ellipse)
        #
        self.ValueFocusNeg = Text(self,self.focus, WIDTH // 2 - 650,100,0) # 1 for -c, 0 for c
        self.ValueFocusPos = Text(self,self.focus, WIDTH // 2 + 550,100,1)

    def Run(self):
        """Главный цикл программы"""

        while True:
            pg.display.set_caption(f"FPS: {self.clock.get_fps()}")
            #
            self.screen.fill('Black')
            self.ellipse.run()
            self.focus.draw_focuses()
            self.coordinates.draw()
            #
            self.ValueFocusPos.translate_value()
            self.ValueFocusNeg.translate_value()
            #
            render = self.font.render(f"2a =  {2 * abcyx}", True, 'blue', 'white')
            self.screen.blit(render, (WIDTH // 2 - 70, 50))
            #
            for event in pg.event.get():
                self.ellipse.control(event)
            pg.display.flip()
            self.clock.tick(10)

if __name__ == '__main__':
    app = App()
    app.Run()
