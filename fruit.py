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
        self.size = fruit_data[name][index].get_size()
    
    def show(self,angle, win):
        self.angle = angle
        win.blit(pygame.transform.rotate(self.pic, self.angle), (self.x, self.y))
    
    #Movimiento de fruta
    def move(self):
        self.y = self.y - (self.u*self.t)
        self.u = self.u + (self.g*self.t)
        self.t = self.t + 0.01
        if self.pos <= 200:
            self.x = self.x + 1.3
        if self.pos > 200:
            self.x = self.x - 1.3
        if self.u == 0:
            self.t = 0
    
    def is_inside(self, finger_pos):
        if self.inside((finger_pos[0] + 13, finger_pos[1] + 13)):
            return True
        if self.inside((finger_pos[0] - 13, finger_pos[1] + 13)):
            return True
        if self.inside((finger_pos[0] + 13, finger_pos[1] - 13)):
            return True
        if self.inside((finger_pos[0] - 13, finger_pos[1] - 13)):
            return True
        return False

    def inside(self, finger_pos):
        up = finger_pos[1] <= self.y + self.size[1]/2
        down = finger_pos[1] >= self.y - self.size[1]/2
        right = finger_pos[0] <= self.x + self.size[0]/2
        left = finger_pos[0] >= self.x - self.size[0]/2
        return up and down and right and left

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
    pos = randint(50, width + 50)
    ypos = randint(height, height + 40)
    gravedad = randint(15, 18)
    name = random.choice(names)
    return fruit_img(pos, ypos, name, 0, gravedad * -0.01)
