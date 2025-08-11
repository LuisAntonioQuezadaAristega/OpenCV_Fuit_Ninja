import pygame
import cv2
from random import randint
import pygame.surfarray
import numpy as np
import mediapipe as mp
import math
import time
import fruit as fr

def distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    d = math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
    return int(d)

pygame.init()
myfont = pygame.font.SysFont("monospace", 24)

cap = cv2.VideoCapture(0)
run, img = cap.read()
height, width, c = img.shape

window_Matrix = np.zeros((height, width)) #Matriz de la imagen de la ventana
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fruit Ninja")

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

slash = np.array([[]], np.int32)
slash_Color = (255, 255, 255)
slash_length = 19
empty_background = np.zeros(shape=(height,width,3), dtype="uint8")

# --- Variables para medir la velocidad ---
prev_pos = None
prev_time = None
max_speed_kmh = 0.0
warning_end_time = 0
# Umbral de velocidad en km/h. Puedes ajustar este valor.
SPEED_THRESHOLD_KMH = 10
# Estimación del ancho de la vista de la cámara en metros (ajustar para precisión)
REAL_WORLD_WIDTH_METERS = 0.5

#Variables para mostrar frutas
fruits = [] #Guarda las frutas en pantalla
angle = 0
contador = 10
limite = 10
score = 0

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    img = cv2.flip(img, 1)
    img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img.flags.writeable = False
    results = hands.process(img2)
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    current_time = time.time()
    index_pos = None

    img_estela = empty_background.copy()

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            #mp_drawing.draw_landmarks(
            #    img,
            #    hand_landmarks,
            #    mp_hands.HAND_CONNECTIONS,
            #    mp_drawing_styles.get_default_hand_landmarks_style(),
            #    mp_drawing_styles.get_default_hand_connections_style())

            # Obtener la posición del dedo índice (landmark 8)
            lm = hand_landmarks.landmark[8]
            index_pos = (int(lm.x * width), int(lm.y * height))

            # --- Lógica de velocidad ---
            if prev_pos is not None and prev_time is not None:
                delta_t = current_time - prev_time
                if delta_t > 0:
                    dist_pixels = distance(index_pos, prev_pos)
                    pixels_per_meter = width / REAL_WORLD_WIDTH_METERS
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

    # Muestra al jugador
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    surface = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
    win.blit(surface, (0, 0))

    # Inicia el juego al detectar el dedo abajo
    if index_pos and contador >= 10 and len(fruits) == 0 and index_pos[1] >= 400:
        print(index_pos)
        contador = 0  
        score = 0

    # Crea las frutas con posiciones y gravedad aleatoria
    if len(fruits) < 3:
        if contador <= limite:
            number_of_fruits = randint(0, 2)
        
        # Resta si se excede del limite
        while(contador+number_of_fruits > limite):
            number_of_fruits -= 1
        
        # Añade las frutas al array de frutas
        for i in range(number_of_fruits):
            fruits.append(fr.generate_fruits(height, width))
            contador += 1
            print(contador)


    # Actualiza la posicion de las frutas
    for fruit in fruits:
        touch = False
        if index_pos and not fruit.touched:
            touch = fruit.is_inside(index_pos)
        
        fruit.move()
        fruit.show(angle, win)
        # mask = pygame.mask.from_surface(fruit.pic)

        if not fruit.touched:
            if index_pos:
                touch = touch or fruit.is_inside(index_pos)
            if touch:
                score = score + 100
                print("score "+ str(score))
                fruits.append(fruit.divide())

        if fruit.y > height + 41:
            fruits.remove(fruit)
    
    # Actualiza el angulo
    angle = angle + 0.2
    if angle == 259:
        angle = 0

    # Muestra la estela en el dedo
    surface = pygame.surfarray.make_surface(np.transpose(img_estela, (1, 0, 2)))
    surface.set_colorkey((0, 0, 0))  #Hace transparente el color negro en la imagen de la estela
    win.blit(surface, (0, 0))
    pygame.display.update()

    success, img = cap.read()
    if not success:
        print("skipping frame")
        continue

cap.release()
cv2.destroyAllWindows()