import cv2
import mediapipe as mp
import math
import numpy as np
import time

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

def distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    d = math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
    return int(d)

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
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
            cv2.circle(img, index_pos, 18, slash_Color, -1)
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
        cv2.polylines(img, [slash_reshaped], False, slash_Color, 15, 0)

    # Mostrar advertencia si el temporizador está activo
    if current_time < warning_end_time:
        cv2.putText(img, "Mueve el dedo mas despacio", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("demo", img)

    key = cv2.waitKey(1)
    if key == 27: # Tecla Esc
        break

cap.release()
cv2.destroyAllWindows()