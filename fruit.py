import pygame
from random import randint
import random

# Guarda las imagenes en un diccionario
# Key = nombre de la fruta, value = array de 3 imagenes
names = ["apple", "peach", "strawberry", "watermelon"]
fruit_data = {}
for name in names:
    fruit_data[name] = [
        pygame.image.load('assets/' + name + '.png'),
        pygame.image.load('assets/' + name + '-1.png'),
        pygame.image.load('assets/' + name + '-2.png')
    ]

health = [
    pygame.transform.scale(pygame.image.load('assets/health/x1.png'), (46,40)),
    pygame.transform.scale(pygame.image.load('assets/health/x2.png'), (52,50)),
    pygame.transform.scale(pygame.image.load('assets/health/x3.png'), (60,60)),

    pygame.transform.scale(pygame.image.load('assets/health/xf1.png'), (46,40)),
    pygame.transform.scale(pygame.image.load('assets/health/xf2.png'), (52,50)),
    pygame.transform.scale(pygame.image.load('assets/health/xf3.png'), (60,60)),
]
game_over = pygame.image.load('assets/gui/game-over.png')
arcade = pygame.transform.scale(pygame.image.load('assets/gui/arcade.png'), (150,150))
quit = pygame.transform.scale(pygame.image.load('assets/gui/quit.png'), (120,120))
bomb = pygame.image.load('assets/bomb.png')
watermelon = pygame.image.load('assets/watermelon.png')

# Clase donde se define las propiedades de las frutas
class fruit_img(object):
    def __init__(self, x, y, name, index, g, u=12, t=0, touched=False):
        self.x = x
        self.y = y
        self.name = name
        self.pic = fruit_data[name][index]
        self.u = u
        self.pos = x
        self.g = g
        self.t = t
        self.touched = touched
        #self.size = fruit_data[name][index].get_size()
        self.centerX = fruit_data[name][index].get_size()[0]/2
        self.centerY = fruit_data[name][index].get_size()[1]/2
        self.radious = (fruit_data[name][index].get_size()[0] + fruit_data[name][index].get_size()[1])/4
    
    def show(self, angle, win):
        self.angle = angle
        win.blit(pygame.transform.rotate(self.pic, self.angle), (self.x, self.y))
    
    #Movimiento de fruta
    def move(self):
        self.y = self.y - (self.u*self.t)
        self.u = self.u + (self.g*self.t)
        self.t = self.t + 0.03
        if self.pos <= 200:
            self.x = self.x + 1.3
        if self.pos > 200:
            self.x = self.x - 1.3
        if self.u == 0:
            self.t = 0
    
    def image_center(self):
        return (self.x + self.centerX, self.y + self.centerY)

    def divide(self):
        dist = 9
        new = fruit_img(self.x - dist, self.y - dist, self.name, 2, self.g, self.u, self.t, touched=True)
        self.x = self.x + dist
        self.y = self.y + dist
        self.pos = self.x
        self.pic = fruit_data[self.name][1]
        self.touched = True
        return new

# Crea y retorna una fruta con posiciones y gravedad aleatoria
def generate_fruits(height, width):
    pos = randint(50, width - 50)
    ypos = randint(height, height + 40)
    gravedad = randint(15, 18)
    name = random.choice(names)
    return fruit_img(pos, ypos, name, 0, gravedad * -0.01)

def draw_buttons(win, end):
    win.blit(arcade, (150, 310))
    win.blit(watermelon, (180, 345))
    win.blit(quit, (350, 330))
    win.blit(bomb, (375, 350))
    
    if end:
        win.blit(game_over, (80, 120))

def show_lives(win, lives):
    win.blit(health[0], (450, 10))
    win.blit(health[1], (500, 10))
    win.blit(health[2], (560, 10))

    if lives < 3:
        win.blit(health[3], (450, 10))
    if lives < 2:
        win.blit(health[4], (500, 10))
    if lives < 1:
        win.blit(health[5], (560, 10))
    