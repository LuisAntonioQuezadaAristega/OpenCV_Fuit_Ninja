import cv2
import mediapipe as mp
import math
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

slash = np.array([[]], np.int32)
slash_Color = (255, 255, 255)
slash_length = 19

w = h = 0

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

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            for id, lm in enumerate(hand_landmarks.landmark):
                if id == 8:
                    index_pos = (int(lm.x * w), int(lm.y * h))
                    cv2.circle(img, index_pos, 18, slash_Color, -1)
                    slash = np.append(slash, index_pos)

                    while len(slash) >= slash_length:
                        slash = np.delete(slash, len(slash) - slash_length, 0)

    slash = slash.reshape((-1, 1, 2))
    cv2.polylines(img, [slash], False, slash_Color, 15, 0)

    cv2.imshow("demo", img)

    #Termina presionando la tecla Esc
    key = cv2.waitKey(33)
    if (key==27):
        break

cap.release()
cv2.destroyAllWindows()
