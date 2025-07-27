import pygame
import cv2
from random import randint
import time
import random
import os

pygame.init()
fruits = [] #Guarda las frutas en pantalla
myfont = pygame.font.SysFont("monospace", 24)

widht = 640
height = 480
win = pygame.display.set_mode((widht, height))
pygame.display.set_caption("Fruit Ninja")

#Se cargan las imagenes de las frutas
apple = [pygame.image.load('images/apple.png'), pygame.image.load('images/apple-1.png'), pygame.image.load('images/apple-2.png')]
peach = [pygame.image.load('images/peach.png'), pygame.image.load('images/peach-1.png'), pygame.image.load('images/peach-2.png')]
strawberry = [pygame.image.load('images/strawberry.png'), pygame.image.load('images/strawberry-1.png'), pygame.image.load('images/strawberry-2.png')]
watermelon = [pygame.image.load('images/watermelon.png'), pygame.image.load('images/watermelon-1.png'), pygame.image.load('images/watermelon-2.png')]

#Classe donde se define las propiedades de las frutas
class img(object):
    def __init__(self, x, y, pic, g, u=12, t=0):
        self.x = x
        self.y = y
        self.pic = pic
        self.u = u
        self.pos = x
        self.g = g * -0.01
        self.t = t
    def show(self,angle):
        self.angle = angle
        win.blit(pygame.transform.rotate(self.pic, self.angle), (self.x, self.y))

run = True
angle = 0

while run:
    number_of_fruits = randint(0, 2)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    #Crea las frutas con posiciones y gravedad aleatoria
    if len(fruits) < 3:
        for i in range(number_of_fruits):
            pos = randint(50, widht + 50)
            ypos = randint(height, height + 40)
            gravedad = randint(15, 18)
            image = random.choice([apple, peach, strawberry, watermelon])

            fruit = image[0]
            fruits.append(img(pos, ypos, fruit, gravedad))

    #Actualiza la posicion de las frutas
    for fruit in fruits:
        fruit.y = fruit.y - (fruit.u*fruit.t)
        fruit.u = fruit.u + (fruit.g*fruit.t)
        fruit.t = fruit.t + 0.001
        if fruit.pos <= 200:
            fruit.x = fruit.x + 0.26
        if fruit.pos > 200:
            fruit.x = fruit.x - 0.26
        if fruit.u == 0:
            fruit.t = 0
        fruit.show(angle)
        mask = pygame.mask.from_surface(fruit.pic)
        if fruit.y > height + 41:
            fruits.remove(fruit)

    pygame.display.update()
    win.fill("black") #Evita que el fondo se llene de imagenes de frutas

    angle = angle + 0.2
    if angle == 259:
        angle = 0
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

pygame.quit()
cv2.destroyAllWindows()
