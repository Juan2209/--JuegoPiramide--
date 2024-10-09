#Archivo para probar con monedero

import pygame
import serial
import time
import subprocess
import mediapipe as mp
import cv2
import math

# Inicializar Pygame
pygame.init()

cap_width = 640
cap_height = 360


# Dimensiones de la ventana

ANCHO = 1300
ALTO = 850

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 128, 255)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
CAFE = (188, 104, 67)
VERDE = (59, 202, 37)
# Variables
coin = False
piramide_held = False
piramide_released = False

# Crear ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Menú Principal")

# Fuente
fuente = pygame.font.Font(None, 40)

# Comunicación con Arduino (Comentado para que no dependa de él)
arduino = serial.Serial('COM3', 9600)
time.sleep(2)

# Inicializar Mediapipe para la detección de manos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Captura de video desde la webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)  # Establece el ancho del cuadro de video en 640 píxeles.
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)  # Establece la altura del cuadro de video en 360 píxeles.
# Cargar la imagen de la pirámide
#piramide_img = pygame.image.load('piramide.png')
#piramide_img = pygame.transform.scale(piramide_img, (100, 100))
#piramide_rect = piramide_img.get_rect()
#piramide_rect.center = (500, 500)

# Cargar una imagen de fondo
fondo_img = pygame.image.load('fondo/piramidesinicial.jpg')
fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))

# Definir la zona activa
#zona_activa = pygame.Rect(850, 500, 300, 80)

# Función para mostrar texto en la pantalla
def mostrar_texto(texto, x, y, color):
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, (x, y))

# Función para mostrar texto centrado en el rectángulo
def mostrar_texto_centrado(texto, rectangulo, color):
    superficie = fuente.render(texto, True, color)
    text_rect = superficie.get_rect(center=rectangulo.center)
    pantalla.blit(superficie, text_rect)

#funcion para el puño cerrado
def detect_finger_down(hand_landmarks):
    finger_down = False
    x_base1 = int(hand_landmarks.landmark[0].x * cap_width)
    y_base1 = int(hand_landmarks.landmark[0].y * cap_height)
    x_pulgar = int(hand_landmarks.landmark[4].x * cap_width)
    y_pulgar = int(hand_landmarks.landmark[4].y * cap_height)
    x_anular = int(hand_landmarks.landmark[16].x * cap_width)
    y_anular = int(hand_landmarks.landmark[16].y * cap_height)
    x_medio = int(hand_landmarks.landmark[12].x * cap_width)
    y_medio = int(hand_landmarks.landmark[12].y * cap_height)

    p1 = (x_base1, y_base1)
    p2 = (x_pulgar, y_pulgar)
    p3 = (x_anular, y_anular)
    p4 = (x_medio, y_medio)
    d_base_pulgar = calc_distance(p1, p2)
    d_base_anular = calc_distance(p1, p3)
    d_base_medio = calc_distance(p1, p4)
    print(d_base_pulgar)
    print(d_base_anular)
    print(d_base_medio)
    if d_base_anular < 30 and d_base_medio < 30 and d_base_pulgar < 60:
        finger_down = True
    print("---------------------")
    print("Puño detectado!")
    return finger_down




# Función para ejecutar el juego (dependiendo de la moneda)
def ejecutar_juego():
    global coin, cap

    # Verificar si el usuario ha insertado la moneda
    if coin:
        # Liberar la cámara antes de ejecutar el segundo script
        cap.release()  
        cv2.destroyAllWindows()  # Destruir ventanas abiertas por OpenCV
        
        # Ejecutar el segundo script (juego.py)
        subprocess.run(['python', '1.py'])
        
        # Reiniciar la variable coin a False después de ejecutar el juego
        coin = False
        print("Juego finalizado. Coin se ha puesto en False.")
        
        # Volver a capturar la cámara
        cap.open(0)
    else:
        print("No puedes ejecutar el juego, la variable coin debe ser True.")

# Inicialización de la cámara (solo si es necesario en tu caso)
cap = cv2.VideoCapture(0)
# Función para verificar el estado de la moneda desde Arduino
def verificar_moneda():
    global coin
    if arduino.in_waiting > 0:
        resultado = arduino.readline().decode('utf-8').strip()
        if resultado == "COIN":
            print("Moneda insertada")
            coin = True
        else:
            print("Moneda no insertada")
            coin = False

# Función para calcular la distancia entre dos puntos
def calc_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Convertir una imagen de OpenCV a Pygame
def cvimage_to_pygame(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_surface = pygame.image.frombuffer(image_rgb.tobytes(), image_rgb.shape[1::-1], 'RGB')
    return image_surface

# Función para mostrar el menú
def mostrar_menu():
    global coin, piramide_held, piramide_released
    corriendo = True
    fist_detected = False
    fist_start_time = None
    fist_duration = 2  # Duración en segundos para mantener el puño cerrado
    game_starting = False
    game_start_time = None
    while corriendo:
        # Leer la imagen desde la webcam
        ret, frame = cap.read()
        if not ret:
            break
        
        # Procesar la imagen de la cámara
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = hands.process(frame_rgb)

        # Convertir la imagen de OpenCV a Pygame y mostrarla
        frame_surface = cvimage_to_pygame(frame)
        pantalla.blit(frame_surface, (0, 0))

        # Dibujar la imagen de fondo
        pantalla.blit(fondo_img, (0, 0))
        if coin:
            mostrar_texto("Cierra el puño por 3 segundos", 330, 300, CAFE)
        
            # Verificar si hay manos detectadas
            if resultado.multi_hand_landmarks:
                for hand_landmarks in resultado.multi_hand_landmarks:
                    # Detectar si el puño está cerrado
                    if detect_finger_down(hand_landmarks):
                        if not fist_detected:
                            fist_detected = True
                            fist_start_time = time.time()
                        elif time.time() - fist_start_time >= fist_duration:
                            print("Puño cerrado detectado por 2 segundos. Iniciando juego...")
                            game_starting = True
                            game_start_time = time.time()
                            fist_detected = False
                            fist_start_time = None
                    else:
                        fist_detected = False
                        fist_start_time = None
        # Mostrar mensaje de "Iniciando juego" por 3 segundos
        if game_starting:
            mostrar_texto("HOLA!!!! TE HE DETECTADO", 460, 520, VERDE)
            mostrar_texto("ABRE Y CIERRA EL PUÑO NUEVAMENTE POR 3 SEGUNDOS", 460, 560, VERDE)
            if time.time() - game_start_time >= 3:
                game_starting = False
                ejecutar_juego()
        #pygame.draw.rect(pantalla, AMARILLO, zona_activa, border_radius=15)
        #mostrar_texto_centrado("Inicio del Juego", zona_activa, NEGRO)

        # Verificar si hay manos detectadas
        if resultado.multi_hand_landmarks:
            for hand_landmarks in resultado.multi_hand_landmarks:
                # Obtener las posiciones de los dedos relevantes
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                # Convertir las coordenadas normalizadas a píxeles
                thumb_pixel = mp_drawing._normalized_to_pixel_coordinates(thumb_tip.x, thumb_tip.y, ANCHO, ALTO)
                index_pixel = mp_drawing._normalized_to_pixel_coordinates(index_tip.x, index_tip.y, ANCHO, ALTO)
                middle_pixel = mp_drawing._normalized_to_pixel_coordinates(middle_tip.x, middle_tip.y, ANCHO, ALTO)

                if thumb_pixel and index_pixel and middle_pixel:
                    # Calcular la distancia entre el pulgar e índice
                    thumb_index_distance = calc_distance(thumb_pixel, index_pixel)

                    # Calcular la distancia entre el índice y el dedo medio
                    index_middle_distance = calc_distance(index_pixel, middle_pixel)

                    # Si el pulgar y el índice están cerca, "agarrar" la pirámide
#                    if thumb_index_distance < 50:
#                        piramide_held = True
#                        piramide_rect.center = index_pixel
#                    else:
#                        piramide_held = False

                    # Si el dedo medio está cerca del índice y la pirámide está en la zona activa, "soltar" la pirámide
                    if index_middle_distance < 30 and piramide_held:
                        piramide_held = False
                        #piramide_released = zona_activa.collidepoint(piramide_rect.center)

        # Si la pirámide se ha soltado en la zona activa, tomar acción
        if piramide_released:
            print("¡Pirámide soltada en la zona activa!")
            ejecutar_juego()
            piramide_released = False

        # Dibujar la pirámide sobre la pantalla
#        pantalla.blit(piramide_img, piramide_rect)

        # Verificar el estado de la moneda (omitido porque siempre será True)
        verificar_moneda()
        mostrar_texto(f"Moneda: {'Aceptada' if coin else 'Inserte moneda'}", 850, 470, AZUL)
        #print(f"Moneda: {'Aceptada' if coin else 'Inserte moneda'}")

        # Mostrar instrucciones para iniciar el juego
        #mostrar_texto("Cierra el puño por 2 segundos para iniciar el juego", 560, 520, CAFE)

        # Actualizar la pantalla de Pygame
        pygame.display.flip()

        # Manejar eventos de Pygame
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    ejecutar_juego()
                elif evento.key == pygame.K_2:
                    corriendo = False

    # Cerrar todo al salir
    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

# Ejecutar el menú
if __name__ == "__main__":
    try:
        mostrar_menu()
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
    finally:
        # Cerrar la conexión con Arduino (comentado)
        arduino.close()  # Comentado porque no usamos Arduino
        hands.close()