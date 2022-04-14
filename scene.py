from OpenGL.GL import *
from OpenGL.GLUT import *
from random import randrange, choices, randint, uniform

from config import *

import math

class Scene:
    def __init__(self):
        self.wsize = wsize
        self.time = "night" or "day"
        self.seconds = 86400
        self.background = Background()
        self.stars = [Star(x, y) for x, y in zip(choices(range(0, self.wsize[0]), k=100),
                                    choices(range(0, self.wsize[1]-100), k=100))]
        self.fireflies = [Firefly(x, y) for x, y in zip(choices(range(*firefly_range[0]), k=25),
                                    choices(range(*firefly_range[1]), k=25))]
        self.moon = Moon(moon_radius, moon_position, moon_color)
        self.sun = Sun(sun_radius, sun_position, sun_color, draw=False)
        self.grasses = [Grass(x, wsize[1], 7) for x in range(0, wsize[0], randint(1, 2))]
        self.house = House()

    def draw(self):
        self.background.draw()
        
        for star in self.stars:
            star.draw()
        
        for grass in self.grasses:
            grass.draw()
        
        for firefly in self.fireflies:
            firefly.draw()
        
        self.house.draw()
        self.moon.draw()
        self.sun.draw()
        self.time_elapse()
    
    def time_elapse(self):
        if self.time == "day":
            if self.sun.revolve():
                self.switch_time()
        else:
            self.seconds -= 250
            if self.seconds < 0:
                self.seconds = 86400
                self.switch_time()
        
        self.background.change_brightness(self.sun, self.time, self.seconds)
        self.sun.change_brightness(self.sun, self.time, self.seconds)
        self.moon.change_brightness(self.sun, self.time, self.seconds)

    def switch_time(self):
        self.time = "day" if self.time == "night" else "night" 

        self.background.switch_time(self.time)
        for star in self.stars:
            star.switch_time(self.time)

        for grass in self.grasses:
            grass.switch_time(self.time)
        
        for firefly in self.fireflies:
            firefly.switch_time(self.time)
        
        self.moon.switch_time()
        self.sun.switch_time()
        self.house.switch_time(self.time)

class Grass:
    def __init__(self, x, y, points):
        self.breakpoints = [0] + [x for x in choices(range(grass_length//points), k=points)]
        self.sway = [randint(-1, 1) for _ in range(points)]
        self.x, self.y = x, y
        self.color = grass_night_color
    
    def breeze(self):
        pass

    def draw(self):
        glBegin(GL_LINES)
        glColor3f(*self.color)
        x, y = self.x, self.y
        for b, s in zip(self.breakpoints, self.sway):
            x += s
            y -= b
            glVertex2f(x, y)
        glEnd()
    
    def switch_time(self, time):
        self.color = grass_night_color if time == "night" else grass_day_color

class Background:
    def __init__(self):
        self.width, self.height = wsize
        self.color = night_sky
        self.bright = 1
        self.switching = False

    def draw(self):
        glBegin(GL_QUADS)
        h = self.height / step
        g = self.color[1] / step
        b = self.color[2] / step
        for i in range(1, step+1):
            glColor3f(self.color[0], self.color[1]-i*g*self.bright, self.color[2]-i*b*self.bright)
            glVertex2f(0, h*i)
            glVertex2f(self.width, h*i)
            glVertex2f(self.width, h*(i-1))
            glVertex2f(0, h*(i-1))
        glEnd()
    
    def switch_time(self, time):
        self.bright =  1 if time == "night" else 0.5
    
    def brighten(self, g, b):
        if g < day_sky[1]:
            g += 0.002
        if b < day_sky[2]:
            b += 0.002
        return g, b
    
    def darken(self, g, b):
        if g > night_sky[1]:
            g -= 0.01
        if b > night_sky[2]:
            b -= 0.01
        return g, b
    
    def change_brightness(self, sun, time, seconds):
        r,g,b = self.color
        if time == "day":
            if r > day_sky[0]:
                r -= 0.0002
                g, b = self.brighten(g, b)
            if sun.x > 1000:
                r += 0.005
                g, b = self.darken(g, b)
                
        else:
            if seconds > 60000:
                if r > night_sky[0]:
                    r -= 0.01
                g, b = self.darken(g, b)

            if seconds < 10000:
                r += 0.005
                g, b = self.brighten(g, b)
        self.color = r, g, b 

class HeavenlyBody:
    def __init__(self, radius, position, color, draw=True):
        self.radius = radius
        self.x, self.y = position
        self.color = *color, 0.0
        self.s = 0.05
        self._draw = draw

    def draw(self):
        self.shine()
        self.draw_body()

    def draw_body(self):
        glBegin(GL_POLYGON)
        for i in range(360):
            glColor4f(*self.color)
            cosine= self.radius * math.cos(i) + self.x  
            sine  = self.radius * math.sin(i) + self.y   
            glVertex2f(cosine,sine)
        glEnd()
    
    def shine(self):
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBegin(GL_POLYGON)
        glColor4f(*self.color[:3], 0.05 * self.color[-1])

        for i in range(360):
            cosine= (self.radius * 1.2)* math.cos(i) + self.x  
            sine  = (self.radius * 1.2) * math.sin(i) + self.y   
            glVertex2f(cosine,sine)
        glEnd()
    
    def switch_time(self):
        self._draw = not self._draw
    
    def appear(self):
        r,g,b,a = self.color
        if a <= 1.0:
            a += 0.02
        self.color = r,g,b,a

    def disappear(self, speed=1):
        r,g,b,a = self.color
        if a >= 0.0:
            a -= 0.02 * speed
        self.color = r,g,b,a

### Day Elements ###
class Sun(HeavenlyBody):
    def __init__(self, radius, position, color, draw):
        super().__init__(radius, position, color, draw)
        self.angle = 0
        self.step = 0.00001
    
    def revolve(self):
        ### (cx+(px−cx)cosθ+(cy−py)sinθ,cy+(py−cy)cosθ+(px−cx)sinθ).
        px, py = self.x, self.y
        cx = wsize[0] // 2
        cy = 4*wsize[1]
        self.x = cx + (px - cx) * math.cos(self.angle) + (cy - py) * math.sin(self.angle)
        self.y = cy+(py - cy)*math.cos(self.angle)+(px - cx)*math.sin(self.angle)
        if self.angle >= 360:
            self.angle = 0
        if self.x > wsize[0] + sun_radius:
            self.x, self.y = sun_position
            self.angle = 0
            return True

        self.angle += self.step
    
    def change_brightness(self, sun, time, seconds):
        if time == "day":
            if sun.x > 980:
                self.disappear()
        else:
            if seconds < 20000:
                self.appear()

### Night Elements ###
class Moon(HeavenlyBody):
    def change_brightness(self, sun, time, seconds):
        if time == "day":
            if sun.x > 1190:
                self.appear()
            else:
                self.disappear(speed=0.5)
        if time == "night":
            if seconds < 1000:
                self.disappear(speed=0.5)
            else:
                self.appear()
        
class Firefly:
    def __init__(self, x, y, draw=True):
        self.x, self.y = x, y
        self.speed = uniform(0.005, 0.2)
        self.xi = randint(0, 1)
        self.yi = randint(0, 1)
        self.entropy = randint(3, 7)
        self.pointsize = 2
        self.color = 0.63, 0.615, 0.357
        self._draw = draw
    
    def fly(self):
        if self.x >= firefly_range[0][1]:
            self.xi = 0
        elif self.x <= firefly_range[0][0]:
            self.xi = 1
        
        if self.y >= firefly_range[1][1]:
            self.yi = 0
        elif self.y <= firefly_range[1][0]:
            self.yi = 1
        
        if self.entropy < 0:
            self.xi = randint(0, 1)
            self.yi = randint(0, 1)
            self.entropy = randint(3, 7)
            self.speed = uniform(0.005, 0.2)
            self.color = 0.68, 0.655, 0.407
            self.pointsize = 4
        else:
            self.entropy -= 0.01
            if self.pointsize > 2:
                self.pointsize -= 0.1
                self.color = tuple(map(lambda m: m-0.0025, self.color))
        self.x += +self.speed if self.xi else -self.speed
        self.y += +self.speed if self.yi else -self.speed 
    
    def draw(self):
        glColor3f(*self.color)
        glPointSize(self.pointsize)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()
        self.fly()
    
    def switch_time(self, time):
        self.color = (0.63, 0.655, 0.407) if time == "night" else (0.1, 0.1, 0.1)

class Star:
    def __init__(self, x, y, draw=True):
        self.x, self.y = x, y
        self.width, self.height = wsize
        self.size = randint(1, 3)
        self.lifespan = randint(3, 7)
        self.i = True
        self.step = uniform(0.0001, 0.005)
        self._draw = draw

    def twinkle(self):
        if self.size >= 3 and self.i:
            self.i = False
            self.step = -self.step
        elif self.size <= 1 and not self.i:
            self.i = True
            self.step = -self.step
        
        self.size += self.step

    def draw(self):
        if self._draw:
            glColor3f(1.0, 1.0, 1.0)
            glPointSize(self.size)
            glBegin(GL_POINTS)
            glVertex2f(self.x, self.y)
            glEnd()
            self.twinkle()
    
    def switch_time(self, time):
        self._draw = True if time == "night" else False

class House:
    def __init__(self):
        self.x, self.y = house_position
        self.window_color = house_night_color
    
    def draw_layout(self):
        ### House Structure
        glBegin(GL_POLYGON)
        glColor3f(121/255,172/255,179/255)

        glVertex2f(self.x+140, self.y+120)
        glVertex2f(self.x+140, self.y)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x, self.y+250)
        glVertex2f(self.x+320, self.y+250)
        glVertex2f(self.x+320, self.y+120)
        glVertex2f(self.x+140, self.y+120)

        glEnd()

        ### Garden
        glBegin(GL_POLYGON)
        glColor3f(0.32, 0.5, 0.27)

        glVertex2f(self.x+320, self.y+250)
        glVertex2f(self.x, self.y+250)
        glVertex2f(self.x-15, self.y+270)
        glVertex2f(self.x+335, self.y+270)
        glVertex2f(self.x+320, self.y+250)

        glEnd()
    
    def draw_roof(self):
        glBegin(GL_POLYGON)
        glColor3f(156/255,167/255,174/255)

        glVertex2f(self.x-5, self.y-10)
        glVertex2f(self.x+145, self.y-10)
        glVertex2f(self.x+145, self.y+10)
        glVertex2f(self.x-5, self.y+10)
        glVertex2f(self.x-5, self.y-10)

        glEnd()

        glBegin(GL_POLYGON)

        glVertex(self.x-5, self.y+110)
        glVertex(self.x+325, self.y+110)
        glVertex(self.x+335, self.y+150)
        glVertex(self.x-5, self.y+150)
        glVertex(self.x-5, self.y+110)

        glEnd()

    def draw_window(self, x, y):
        glBegin(GL_POLYGON)
        glColor3f(*self.window_color)

        glVertex2f(x+20, y)
        glVertex2f(x, y)
        glVertex2f(x, y+40)
        glVertex2f(x+20, y+40)
        glVertex2f(x+20, y)

        glEnd()

    def draw_frame(self, x, y, w, h):
        glBegin(GL_POLYGON)
        glColor3f(1, 1, 1)

        glVertex2f(x+w, y)
        glVertex2f(x, y)
        glVertex2f(x, y+h)
        glVertex2f(x+w, y+h)
        glVertex2f(x+w, y)

        glEnd()
    
    def draw_windows(self):
        self.draw_frame(self.x+44, self.y+38, 52, 48)
        x, y = 48, 42
        for _ in range(2):
            self.draw_window(self.x+x, self.y+y)
            x += 24
        
        self.draw_frame(self.x+180, self.y+166, 100, 48)
        x, y = 184, 170
        for _ in range(4):
            self.draw_window(self.x+x, self.y+y)
            x += 24

    def draw_door(self):
        glBegin(GL_POLYGON)
        glColor3f(146/255,68/255,27/255)

        glVertex2f(self.x+90, self.y+180)
        glVertex2f(self.x+50, self.y+180)
        glVertex2f(self.x+50, self.y+250)
        glVertex2f(self.x+90, self.y+250)
        glVertex2f(self.x+90, self.y+180)

        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(1, 1, 1)
        x, y = self.x+70, self.y+200
        for i in range(360):
            cosine= 12 * math.cos(i) + x  
            sine  = 12 * math.sin(i) + y   
            glVertex2f(cosine,sine)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(*self.window_color)
        x, y = self.x+70, self.y+200
        for i in range(360):
            cosine= 10 * math.cos(i) + x  
            sine  = 10 * math.sin(i) + y   
            glVertex2f(cosine,sine)
        glEnd()

    def switch_time(self, time):
        self.window_color = house_night_color if time == "night" else house_day_color

    def draw(self):
        self.draw_layout()
        self.draw_roof()
        self.draw_windows()
        self.draw_door()
        