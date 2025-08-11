import pygame
import cv2
from random import randint
import random
import pygame.surfarray
from PIL import Image
import numpy as np
import mediapipe as mp
import math
import time
#import fruit

#Clase donde se define las propiedades de las frutas
class fruit_img(object):
    def __init__(self, x, y, pic, g, size, u=12, t=0):
        self.x = x
        self.y = y
        self.pic = pic
        self.u = u
        self.pos = x
        self.g = g * -0.01
        self.t = t
        self.touched = False
        self.size = size
    def show(self,angle):
        self.angle = angle
        win.blit(pygame.transform.rotate(self.pic, self.angle), (self.x, self.y))

def distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    d = math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
    return int(d)

def inside_circle(finger_pos, fruit_pos, size):
    point = (fruit_pos[0] + size[0], fruit_pos[1] + size[1])
    if is_inside(finger_pos, point):
        return True
    point = (fruit_pos[0] - size[0], fruit_pos[1] + size[1])
    if is_inside(finger_pos, point):
        return True
    point = (fruit_pos[0] + size[0], fruit_pos[1] - size[1])
    if is_inside(finger_pos, point):
        return True
    point = (fruit_pos[0] - size[0], fruit_pos[1] - size[1])
    if is_inside(finger_pos, point):
        return True
    return False

def is_inside(finger_pos, point):
    up = point[1] <= finger_pos[1] + 13
    down = point[1] >= finger_pos[1] - 13
    right = point[0] <= finger_pos[0] + 13
    left = point[0] >= finger_pos[0] - 13
    return up and down and right and left

pygame.init()
fruits = [] #Guarda las frutas en pantalla
fruits_parts = [] #Guarda las frutas partidas
myfont = pygame.font.SysFont("monospace", 24)

widht = 640
height = 480
window_Matrix = np.zeros((height, widht)) #Matriz de la imagen de la ventana
win = pygame.display.set_mode((widht, height))
pygame.display.set_caption("Fruit Ninja")

#Se cargan las imagenes de las frutas
apple = [pygame.image.load('assets/apple.png'), pygame.image.load('assets/apple-1.png'), pygame.image.load('assets/apple-2.png')]
peach = [pygame.image.load('assets/peach.png'), pygame.image.load('assets/peach-1.png'), pygame.image.load('assets/peach-2.png')]
strawberry = [pygame.image.load('assets/strawberry.png'), pygame.image.load('assets/strawberry-1.png'), pygame.image.load('assets/strawberry-2.png')]
watermelon = [pygame.image.load('assets/watermelon.png'), pygame.image.load('assets/watermelon-1.png'), pygame.image.load('assets/watermelon-2.png')]

fruit_data = []
for fruit_png in [apple, peach, strawberry, watermelon]:
    png = fruit_png[0]
    fruit_data.append({
        "size": (png.get_height()/2, png.get_width()/2),
        "images": fruit_png
    })

empty_background = np.zeros(shape=(480,640,3), dtype="uint8")

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

slash = np.array([[]], np.int32)
slash_Color = (255, 255, 255)
slash_length = 19

w = h = 0

# --- Variables para medir la velocidad ---
prev_pos = None
prev_time = None
max_speed_kmh = 0.0
warning_end_time = 0
# Umbral de velocidad en km/h. Puedes ajustar este valor.
SPEED_THRESHOLD_KMH = 10
# Estimación del ancho de la vista de la cámara en metros (ajustar para precisión)
REAL_WORLD_WIDTH_METERS = 0.5

run = True
angle = 0
contador = 0
limite = 10

cap = cv2.VideoCapture(0)
print("inicio")
unavez = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    success, img = cap.read()
    if not success:
        print("skipping frame")
        continue

    h, w, c = img.shape
    img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
    img.flags.writeable = False
    results = hands.process(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    current_time = time.time()
    index_pos = None

    img_estela = empty_background.copy()

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            # Obtener la posición del dedo índice (landmark 8)
            lm = hand_landmarks.landmark[8]
            index_pos = (int(lm.x * w), int(lm.y * h))

            if contador >= 10 and index_pos[1] >= 400:
                print(index_pos)
                contador = 0

            # --- Lógica de velocidad ---
            if prev_pos is not None and prev_time is not None:
                delta_t = current_time - prev_time
                if delta_t > 0:
                    dist_pixels = distance(index_pos, prev_pos)
                    pixels_per_meter = w / REAL_WORLD_WIDTH_METERS
                    dist_meters = dist_pixels / pixels_per_meter
                    speed_mps = dist_meters / delta_t
                    speed_kmh = speed_mps * 3.6

                    if speed_kmh > max_speed_kmh:
                        max_speed_kmh = speed_kmh

                    if speed_kmh > SPEED_THRESHOLD_KMH:
                        warning_end_time = current_time + 1  # Mostrar advertencia por 1 segundo
                        print(f"Velocidad excesiva detectada. Máxima velocidad registrada: {max_speed_kmh:.2f} km/h")

            # Actualizar la posición y el tiempo para el siguiente fotograma
            prev_pos = index_pos
            prev_time = current_time
            # --- Fin de la lógica de velocidad ---

            # Dibujar la estela
            cv2.circle(img_estela, index_pos, 18, slash_Color, -1)
            slash = np.append(slash, index_pos)
            while len(slash) >= slash_length:
                slash = np.delete(slash, len(slash) - slash_length, 0)
    else:
        # Si no se detecta la mano, reiniciar la posición y la estela
        if prev_pos is not None:
            slash = np.array([[]], np.int32) # Limpiar estela para evitar líneas largas
        prev_pos = None
        prev_time = None
    
    # Dibujar la polilínea de la estela
    if len(slash) > 1:
        slash_reshaped = slash.reshape((-1, 1, 2))
        cv2.polylines(img_estela, [slash_reshaped], False, slash_Color, 15, 0)

    # Mostrar advertencia si el temporizador está activo
    if current_time < warning_end_time:
        cv2.putText(img_estela, "Mueve el dedo mas despacio", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    surface = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
    win.blit(surface, (0, 0))
    #-------------------------------------++

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
            data = random.choice(fruit_data)

            fruit = data["images"][0]
            fruits.append(fruit_img(pos, ypos, fruit, gravedad, data["size"]))
            contador += 1
            print(contador)

    #Actualiza la posicion de las frutas
    for fruit in fruits:
        touch = False
        if index_pos:
            size = fruit.size
            if (angle >= 90 and angle < 180) or (angle >= 270 and angle < 360):
                size = (size[1], size[0])
            touch = inside_circle(index_pos, (fruit.x, fruit.y), size)
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
        pygame.mask.from_surface(fruit.pic)
        if index_pos:
            size = fruit.size
            if (angle >= 90 and angle < 180) or (angle >= 270 and angle < 360):
                size = (size[1], size[0])
            touch = touch or inside_circle(index_pos, (fruit.x, fruit.y), size)

        if not fruit.touched and touch:
            fruit.touched = True

            xposition = fruit.x
            yposition = fruit.y
            grav = fruit.g / -0.01
            vel = fruit.u
            size = fruit.size
            tim = fruit.t
            if fruit.pic == apple[0]:
                fruits_parts.append(fruit_img(xposition +9, yposition + 9, apple[1], grav, size, vel, tim))
                fruits_parts.append(fruit_img(xposition - 9, yposition - 9, apple[2], grav, size, vel, tim))
            elif fruit.pic == peach[0]:
                fruits_parts.append(fruit_img(xposition +9, yposition + 9, peach[1], grav, size, vel, tim))
                fruits_parts.append(fruit_img(xposition - 9, yposition - 9, peach[2], grav, size, vel, tim))
            elif fruit.pic == strawberry[0]:
                fruits_parts.append(fruit_img(xposition +9, yposition + 9, strawberry[1], grav, size, vel, tim))
                fruits_parts.append(fruit_img(xposition - 9, yposition - 9, strawberry[2], grav, size, vel, tim))
            elif fruit.pic == watermelon[0]:
                fruits_parts.append(fruit_img(xposition +9, yposition + 9, watermelon[1], grav, size, vel, tim))
                fruits_parts.append(fruit_img(xposition - 9, yposition - 9, watermelon[2], grav, size, vel, tim))

        if fruit.y > height + 41 or fruit.touched:
            fruits.remove(fruit)
    
    #Actualiza la posicion de las frutas partidas
    for fruit in fruits_parts:
        fruit.y = fruit.y - (fruit.u*fruit.t)
        fruit.u = fruit.u + (fruit.g*fruit.t)
        fruit.t = fruit.t + 0.01
        if fruit.pos <= 200:
            fruit.x = fruit.x + 1.3
        if fruit.pos > 200:
            fruit.x = fruit.x - 1.3
        if fruit.u == 0:
            fruit.t = 0
        fruit.show(angle)
        pygame.mask.from_surface(fruit.pic)
        if fruit.y > height + 41:
            fruits_parts.remove(fruit)
    
    angle = angle + 0.2
    if angle == 259:
        angle = 0

    #-------------------------------------++

    surface = pygame.surfarray.make_surface(np.transpose(img_estela, (1, 0, 2)))
    surface.set_colorkey((0, 0, 0))  #Hace transparente el color negro
    win.blit(surface, (0, 0))

    pygame.display.update()

cap.release()
cv2.destroyAllWindows()