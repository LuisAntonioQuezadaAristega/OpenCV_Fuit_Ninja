import pygame
import cv2
from random import randint
import time
import random
import os
from PIL import Image
import numpy as np

pygame.init()
fruits = [] #Guarda las frutas en pantalla
myfont = pygame.font.SysFont("monospace", 24)

widht = 640
height = 480
window_Matrix = np.zeros((height, widht)) #Matriz de la imagen de la ventana
win = pygame.display.set_mode((widht, height))
pygame.display.set_caption("Fruit Ninja")

#Se cargan las imagenes de las frutas
apple = [pygame.image.load('assets/apple.png'), pygame.image.load('assets/apple-1.png'), pygame.image.load(
    'assets/apple-2.png')]
peach = [pygame.image.load('assets/peach.png'), pygame.image.load('assets/peach-1.png'), pygame.image.load(
    'assets/peach-2.png')]
strawberry = [pygame.image.load('assets/strawberry.png'), pygame.image.load('assets/strawberry-1.png'), pygame.image.load(
    'assets/strawberry-2.png')]
watermelon = [pygame.image.load('assets/watermelon.png'), pygame.image.load('assets/watermelon-1.png'), pygame.image.load(
    'assets/watermelon-2.png')]

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

def updateMatrix():
    #Transforma la imagen de la Ventana a String
    raw_str = pygame.image.tostring(win, "RGB")
    image = Image.frombytes("RGB", win.get_size(), raw_str)
    # Convertir a matriz NumPy
    image_array = np.array(image)
    # Cambia de RGB A BGR
    return cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

def getWindowsMatrix():
    return window_Matrix

run = True
angle = 0
contador = 0
limite = 10

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    #Crea las frutas con posiciones y gravedad aleatoria
    if len(fruits) < 3:
        if contador <= limite:
            number_of_fruits = randint(0, 2)
        #Resta si se excede del limite
        while(contador+number_of_fruits > limite):
            number_of_fruits -= 1
        
        for i in range(number_of_fruits):
            pos = randint(50, widht + 50)
            ypos = randint(height, height + 40)
            gravedad = randint(15, 18)
            image = random.choice([apple, peach, strawberry, watermelon])

            fruit = image[0]
            fruits.append(img(pos, ypos, fruit, gravedad))
            contador += 1
            print(contador)

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
    window_Matrix = updateMatrix()
    cv2.imshow("prueba", window_Matrix)
    win.fill("black") #Evita que el fondo se llene de imagenes de frutas

    angle = angle + 0.2
    if angle == 259:
        angle = 0
    
    run = len(fruits) > 0 or contador < limite

pygame.quit()
cv2.destroyAllWindows()
