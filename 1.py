#BUENO
import pygame
import time
import pymunk
import pymunk.pygame_util
import json
import mediapipe as mp
import cv2
import random
from math import sqrt

pygame.init()

settings = open('configuraciones.json')
data = json.load(settings)
settings.close()

objectreadfile = data['mask']
objectRadius = data['radius']
objectColor = (data['rgb'][0],data['rgb'][1],data['rgb'][2],0)
makeoptimize = data["WINDOWS_opt"]
invertPic = data["Inver"]
gcap1 = (data['corner_1'][0],data['corner_1'][1])
gcap2 = (data['corner_2'][0],data['corner_2'][1])
relW = gcap2[0] - gcap1[0]
relH = gcap2[1] - gcap1[1]

playGIF = False
#definimos el tamaño de la ventana 
#para definir el tamaño de la pelota que en esta ocasion es una piramide
#te dirijes al archivo configuraciones.json en la parte de radius defines 
#el tamaño de la piramide en esa ocasion se maneja como radio 
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 850

# Definir el diccionario audios_piramides aquí
audios_piramides = {
    "Chichén Itzá": r"Audios_Piramides/Chichén_Itzá.mp3",
    "Palenque": r"Audios_Piramides/Palenque_Chiapas.mp3",
    "Calakmul": r"Audios_Piramides/Calakmul_Campeche.mp3",
    "Cholula": r"Audios_Piramides/Cholula_Puebla.mp3",
    "Comalcalco": r"Audios_Piramides/Comalcalco_Tabasco.mp3",
    "Mitla": r"Audios_Piramides/Mitla_Oaxaca.mp3",
    "Monte Albán": r"Audios_Piramides/Monte_Albán_Oaxaca.mp3",
    "El Tajín": r"Audios_Piramides/El_Tajín.mp3",
    "Tamtoc": r"Audios_Piramides/Tamtoc_San_Luis_Potosí.mp3",
    "Teotihuacan": r"Audios_Piramides/Teotihuacán_Estado_de_México.mp3",
    "Tulum": r"Audios_Piramides/Tulum_Quintana_Roo.mp3",
    "Xochicalco": r"Audios_Piramides/Xochicalco_Morelos.mp3"
}

# Definir áreas objetivo para colisiones
areas2 = {
    "Chichén Itzá": pygame.Rect(1000, 235, 160, 100),
    "Palenque": pygame.Rect(750, 620, 110, 120),
    "Calakmul": pygame.Rect(950, 380, 110, 130),
    "Cholula": pygame.Rect(340, 470, 80, 80),
    "Comalcalco": pygame.Rect(770, 500, 80, 80),
    "Mitla": pygame.Rect(420, 610, 150, 150),
    "Monte Albán": pygame.Rect(420, 610, 150, 150),
    "El Tajín": pygame.Rect(460, 440, 80, 80),
    "Tamtoc": pygame.Rect(100, 30, 150, 200),
    "Teotihuacan": pygame.Rect(190, 420, 50, 50),
    "Tulum": pygame.Rect(1100, 350, 100, 110),
    "Xochicalco": pygame.Rect(255, 470, 60, 60)
}

# Función para mezclar el orden de las pirámides
def mezclar_piramides(areas2):
    claves = list(areas2.keys())
    random.shuffle(claves)
    nuevo_orden = {clave: areas2[clave] for clave in claves}
    return nuevo_orden

# Llamada a la función
areas = mezclar_piramides(areas2)

# Imprimir el nuevo diccionario para ver el resultado
print(areas)

# Nuevas variables globales
pyramid_released = False
release_time = None
waiting_for_result = False
##################################3
piramides_correctas = 0
total_piramides = len(areas)
current_audio = None


#area_correcta = pygame.Rect(790, 500, 40, 40)#(izquierda/derecha(punto 1), arriba abajo(punto1), izquierda/derecha para definir
#el tamaño(punto 2), arriba/abajo para definir el tamaño (punto 2))
#area_incorrecta = pygame.Rect(920, 603, 951, 628)
# Inicializar sonidos
pygame.mixer.init()
sonido_correcto = pygame.mixer.Sound("sonido/correcto.mp3")
sonido_incorrecto = pygame.mixer.Sound("sonido/incorrecto.mp3")

#funcion para renderizar el texto
def render_text(text, font_size, color):
    font = pygame.font.Font(None, font_size)
    return font.render(text, True, color)

# Renderizado de textos
pyramid_texts = {
    "Calakmul": render_text("Calakmul", 60, (0, 0, 0)),
    "Chichén Itzá": render_text("Chichén Itzá", 60, (20, 0, 0)),
    "Cholula": render_text("Cholula", 60, (0, 0, 0)),
    "Comalcalco": render_text("Comalcalco", 60, (0, 0, 0)),
    "Mitla": render_text("Mitla", 60, (0, 0, 0)),
    "Monte Albán": render_text("Monte Albán", 60, (0, 0, 0)),
    "Palenque": render_text("Palenque", 60, (0, 0, 0)),
    "El Tajín": render_text("El Tajín", 60, (0, 0, 0)),
    "Tamtoc": render_text("Tamtoc", 60, (0, 0, 0)),
    "Teotihuacan": render_text("Teotihuacan", 60, (0, 0, 0)),
    "Tulum": render_text("Tulum", 60, (0, 0, 0)),
    "Xochicalco": render_text("Xochicalco", 60, (0, 0, 0)),
}

# Lista de nombres de pirámides para mantener el orden
pyramid_names = list(areas.keys())
current_pyramid_index = 0

def get_current_pyramid():
    return pyramid_names[current_pyramid_index]

def next_pyramid():
    global current_pyramid_index
    # Incrementar el índice de la pirámide actual
    current_pyramid_index = (current_pyramid_index + 1) % len(pyramid_names)
    # Si el índice vuelve a ser 0, significa que el jugador ha completado todas las pirámides
    if current_pyramid_index == 0:
        pygame.mixer.music.pause()
        return False  # Esto indica que todas las pirámides han sido completadas
    else:
        sonido_correcto.play()
        return True  # Continuar con la siguiente pirámide

# Función para reiniciar el juego después de una colisión correcta
def reset_game():
    global start_time, current_audio
    moving_ball.body.position = (700, 100)
    moving_ball.body.velocity = (0, 0)
    start_time = time.time()
    
    current_pyramid = get_current_pyramid()
    if current_pyramid in audios_piramides:
        pygame.mixer.stop()
        pygame.mixer.music.load(audios_piramides[current_pyramid])
        pygame.mixer.music.play(-1)
        current_audio = current_pyramid
        sonido_correcto.play()
        pygame.mixer.music.play(-1)

# Función principal para manejar la colisión correcta
def handle_correct_collision():
    global game_over, piramides_correctas, current_pyramid_index
    sonido_correcto.play()
    piramides_correctas += 1
    
    if piramides_correctas == total_piramides:
        game_over = True
    else:
        current_pyramid_index = (current_pyramid_index + 1) % len(pyramid_names)
        reset_game()
# Función para reiniciar el juego en colision incorrecta
def reset_game_inc():
    global piramides_correctas, start_time
    #sonido_incorrecto.play()
    # Restablecer la posición de la pelota en movimiento a las coordenadas iniciales
    moving_ball.body.position = (700, 100)
    moving_ball.body.velocity = (0, 0)
    
    # Restablecer la posición visual de la pirámide también
    pyramid_pos = (700 - objectRadius, 100 - objectRadius)
    
    piramides_correctas += 1


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PIRAMIDES DE LA REPUBLICA MEXICANA")

# Cargar la imagen de fondo
background_image = pygame.image.load('fondo/mapaconpunto.png').convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)
draw_options.collision_point_color = (0,0,0,0)
draw_options.constraint_color = (0,0,0,0)

lines = [
    [(0, 0), (0, SCREEN_HEIGHT)],
    [(0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT)],
    [(SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)],
    [(SCREEN_WIDTH, 0), (0, 0)]
]


def create_line(p1, p2, wd):
    # Crear un cuerpo estático para la simulación de física en pymunk
    # Los cuerpos estáticos no se ven afectados por las fuerzas (gravedad, colisiones, etc.)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)

    # Establecer la posición inicial del cuerpo estático (en este caso, en el origen (0, 0))
    body.position = (0, 0)

    # Crear una forma de segmento (línea) utilizando los puntos de inicio y fin (p1 y p2) y el ancho (wd)
    shape = pymunk.Segment(body, p1, p2, wd)

    # Establecer la elasticidad del segmento a 0.8 (rebote moderado en colisiones)
    shape.elasticity = 0.8

    # Añadir el cuerpo y la forma al espacio de simulación de pymunk
    space.add(body, shape)


def create_ball(radius, pos, rgba):
    # Crear un cuerpo para la simulación de física en pymunk
    body = pymunk.Body()

    # Establecer la posición inicial del cuerpo
    body.position = pos

    # Crear una forma circular utilizando el cuerpo y el radio proporcionado
    shape = pymunk.Circle(body, radius)

    # Establecer la masa de la bola a 5 unidades
    shape.mass = 5

    # Establecer la elasticidad de la bola a 1 (choque completamente elástico)
    shape.elasticity = 1

    # Comentar la fricción de la bola (actualmente no se usa)
    # shape.friction = 50

    # Asignar un color RGBA a la bola para fines de visualización
    shape.color = rgba

    # Usar un pivote para añadir fricción al cuerpo
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))

    # Deshabilitar la corrección de la articulación del pivote
    pivot.max_bias = 0

    # Emular la fricción lineal estableciendo una fuerza máxima en la articulación del pivote
    pivot.max_force = 1000

    # Añadir el cuerpo, la forma y el pivote al espacio de simulación de pymunk
    space.add(body, shape, pivot)

    # Devolver la forma creada para su uso posterior
    return shape


def create_hand_circle(position, radius=30, color=(255, 255, 255, 255)):
    # Crear un cuerpo para la simulación de física en pymunk
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = position

    # Crear una forma circular
    shape = pymunk.Circle(body, radius)
    shape.color = color  # Color del círculo (RGBA)

    # Añadir el cuerpo y la forma al espacio de simulación de pymunk
    space.add(body, shape)

    return body, shape


for c in lines:
    create_line(c[0],c[1],0.0)

handsShapes = [None, None]
#en esta parte se cambia la pocision en la cual se desea que se inicialice la primera piramide 
moving_ball = create_ball(round(objectRadius*1.4),(900,100),objectColor)
frametick = 0
frameCount = 0


# Cargar la imagen de la pirámide con transparencia
pic = pygame.image.load(objectreadfile).convert_alpha()
pic = pygame.transform.scale(pic, (objectRadius*2, objectRadius*2))
ballFrame = pic


'''
if playGIF:
    ballFrames = []
    for x in range(16):
        file = "frames/frame_"+str(x)+"_delay-0.05s.gif"
        pic = pygame.image.load(file)
        pic = pygame.transform.scale(pic,(objectRadius*2,objectRadius*2))
        ballFrames.append(pic)
else: 
    pic = pygame.image.load(objectreadfile)
    pic = pygame.transform.scale(pic,(objectRadius*2,objectRadius*2))
    ballFrame = pic
'''
#clock
clock = pygame.time.Clock()
FPS = 30
#colours
BG = (0, 0, 0)
run = True

makefullscreen = True

print("Ejecutando...")


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

if makeoptimize:
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

counter = 0
lastgestureX = 0
lastgestureY = 0
lastgestureZ = 0
moveDelta = 30
lastmoveX = 0
lastmoveY = 0
lastmoveZ = 0
waitframe = True
moveX = 0
moveY = 0
moveZ = 0
newZ = True
refZ = 0
absZ = 0
initialpose = True
zoomcounter = 0

def calc_distance(p1, p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

# Inicializar el temporizador
start_time = time.time()
time_limit = 160  # 40 segundos para cada pirámide
game_over = False

# Iniciar el módulo de detección de manos de MediaPipe con confianza mínima de detección y seguimiento
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened() and run and not game_over:
        clock.tick(FPS)
        space.step(10 / FPS)

        ret, frame = cap.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frameWidth = image.shape[1]
        frameHeight = image.shape[0]

        if invertPic:
            image = cv2.flip(image, 1)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        #se cambia el color del marco de la area de interaccion
        cv2.rectangle(image, gcap1, gcap2, (255, 255, 0), 1)
        totalHands = 0

        # Inicializar variables para el control de la pirámide
        pyramid_held = False
        pyramid_released = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Obtener las posiciones de los dedos relevantes
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                # Convertir las coordenadas normalizadas a píxeles
                thumb_pixel = mp_drawing._normalized_to_pixel_coordinates(thumb_tip.x, thumb_tip.y, frameWidth, frameHeight)
                index_pixel = mp_drawing._normalized_to_pixel_coordinates(index_tip.x, index_tip.y, frameWidth, frameHeight)
                middle_pixel = mp_drawing._normalized_to_pixel_coordinates(middle_tip.x, middle_tip.y, frameWidth, frameHeight)

                if thumb_pixel and index_pixel and middle_pixel:
                    # Calcular la distancia entre el pulgar e índice
                    thumb_index_distance = calc_distance(thumb_pixel, index_pixel)
                    
                    # Calcular la distancia entre el índice y el dedo medio
                    index_middle_distance = calc_distance(index_pixel, middle_pixel)

                    # Si el pulgar y el índice están cerca, mover la pirámide
                    if thumb_index_distance < 50:
                        pyramid_held = True
                        moving_ball.body.position = index_pixel
                        cv2.circle(image, thumb_pixel, 10, (0, 255, 0), -1)
                        cv2.circle(image, index_pixel, 10, (0, 255, 0), -1)
                    else:
                        cv2.circle(image, thumb_pixel, 10, (255, 0, 0), -1)
                        cv2.circle(image, index_pixel, 10, (255, 0, 0), -1)

                    # Si el dedo medio está cerca del índice, soltar la pirámide
                    if index_middle_distance < 30:
                        if not pyramid_released:
                            pyramid_released = True
                            release_time = time.time()
                            waiting_for_result = True
                        cv2.circle(image, middle_pixel, 10, (0, 0, 255), -1)
                    else:
                        cv2.circle(image, middle_pixel, 10, (255, 0, 0), -1)





        if not makefullscreen:
            cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #screen.fill(BG)
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        space.debug_draw(draw_options)

        if frameCount > 15:
            frameCount = 0

        #if playGIF:
        #    screen.blit(ballFrames[frameCount],
        #               (moving_ball.body.position[0] - objectRadius, moving_ball.body.position[1] - objectRadius))
        #else:
        #    screen.blit(ballFrame,
        #                (moving_ball.body.position[0] - objectRadius, moving_ball.body.position[1] - objectRadius))
        # Dibujar la pirámide en su posición actual
        pyramid_pos = (int(moving_ball.body.position[0] - objectRadius), 
               int(moving_ball.body.position[1] - objectRadius))
        screen.blit(ballFrame, pyramid_pos)


        current_pyramid = get_current_pyramid()
        pyramid_text = pyramid_texts[current_pyramid]

        # Manejo del audio
        if current_audio != current_pyramid:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audios_piramides[current_pyramid])
            pygame.mixer.music.play(-1)
            current_audio = current_pyramid

        for pyramid_name, pyramid_rect in areas.items():
            if pyramid_rect.collidepoint(moving_ball.body.position):
                pyramid_text = pyramid_texts[pyramid_name]
                

        text_x = moving_ball.body.position[0] - pyramid_text.get_width() // 2
        text_y = moving_ball.body.position[1] + objectRadius + 5
        #screen.blit(pyramid_text, (text_x, text_y))

                # Lógica para manejar la colisión solo cuando se suelta la pirámide
        # Lógica para manejar la colisión después de esperar 5 segundos
        if waiting_for_result and time.time() - release_time >= 3:
            waiting_for_result = False
            ball_rect = pygame.Rect(moving_ball.body.position[0], moving_ball.body.position[1], 1, 1)
            correct_area = areas[current_pyramid]

            if correct_area.colliderect(ball_rect):
                print(f"¡Colisión correcta con {current_pyramid}!")
                sonido_correcto.play()
                handle_correct_collision()
            else:
                collision_detected = False
                for name, area in areas.items():
                    if area.colliderect(ball_rect):
                        print(f"Colisión incorrecta. La pirámide correcta es {current_pyramid}")
                        sonido_incorrecto.play()
                        game_over = True
                        collision_detected = True
                        break
                if not collision_detected:
                    print("No se detectó colisión con ninguna área.")
                    # Opcional: reproducir un sonido o mostrar un mensaje de que no se colocó en ninguna área

         # Reiniciar el estado si la pirámide se mueve durante la espera
        if waiting_for_result and pyramid_held:
            waiting_for_result = False
            pyramid_released = False
        # Crear superficies transparentes para las áreas una vez
        area_surfaces = {}
        for name, area in areas.items():
            surface = pygame.Surface((area.width, area.height), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0))  # Completamente transparente
            #surface.fill((0, 0, 0))  # Completamente transparente
            pygame.draw.rect(surface, (0, 255, 0, 0), (0, 0, area.width, area.height), 2)  # Borde semi-transparente
            area_surfaces[name] = surface
        for name, area in areas.items():
            color = (255, 255, 255, 0) if name == current_pyramid else (255, 255, 255, 0)
            surface = area_surfaces[name].copy()
            pygame.draw.rect(surface, color, (0, 0, area.width, area.height), 2)  # Actualizar el color del borde
            screen.blit(surface, (area.x, area.y))


        pyramid_text = pyramid_texts[current_pyramid]
        text_x = SCREEN_WIDTH // 2 - pyramid_text.get_width() // 2
        text_y = 50
        screen.blit(pyramid_text, (text_x, text_y))

        instruction_text = render_text(f"Lleva la pirámide al estado que creas correspondiente", 30, (255, 255, 255))
        instruction_x = SCREEN_WIDTH // 2 - instruction_text.get_width() // 2
        instruction_y = 10
        screen.blit(instruction_text, (instruction_x, instruction_y))

        counter_text = render_text(f"PIRÁMIDES CORRECTAS: {piramides_correctas}/{total_piramides}", 30, (255, 255, 255))
        counter_x = SCREEN_WIDTH - counter_text.get_width() - 10
        counter_y = 10
        screen.blit(counter_text, (counter_x, counter_y))

        elapsed_time = time.time() - start_time
        remaining_time = max(0, time_limit - elapsed_time)
        time_text = render_text(f"Tiempo: {int(remaining_time)}s", 30, (0, 0, 255))
        time_x = 10
        time_y = 10
        screen.blit(time_text, (time_x, time_y))

        if remaining_time <= 0 or piramides_correctas == total_piramides:
            pygame.mixer.music.pause()
            game_over = True

        if frametick > 0:
            frametick = 0
            frameCount += 1
        frametick += 1

        pygame.display.update()

    if game_over:
        #screen.fill(BG)
        screen.blit(background_image, (0, 0))
        if piramides_correctas == total_piramides:
            game_over_text = render_text("¡FELICIDADES!", 60, (0, 255, 0))
            text_x = SCREEN_WIDTH // 2 - game_over_text.get_width() // 2
            text_y = SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2
            screen.blit(game_over_text, (text_x, text_y))

            congrats_text = render_text("ACERTASTE TODAS LAS PIRÁMIDES", 40, (0, 0, 255))
            congrats_x = SCREEN_WIDTH // 2 - congrats_text.get_width() // 2
            congrats_y = text_y + game_over_text.get_height() + 20
            screen.blit(congrats_text, (congrats_x, congrats_y))

            gift_text = render_text("TOMA TU OBSEQUIO", 40, (255, 255, 0))
            gift_x = SCREEN_WIDTH // 2 - gift_text.get_width() // 2
            gift_y = congrats_y + congrats_text.get_height() + 40
            screen.blit(gift_text, (gift_x, gift_y))
        else:
            # Definir el texto 'Game Over'
            # Renderizar el texto "Game Over"
            game_over_text = render_text("Game Over", 50, (255, 0, 0))  # Texto "Game Over" con tamaño 50 y color rojo
            
            # Centrar el texto "Game Over" en pantalla
            text_x = SCREEN_WIDTH // 2 - game_over_text.get_width() // 2
            text_y = SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2
            
            # Mostrar el texto "Game Over" en pantalla
            screen.blit(game_over_text, (text_x, text_y))
            
            # Ahora que game_over_text está definido, puedes calcular score_y
            score_y = text_y + game_over_text.get_height() + 5
            
            # Mostrar el texto del puntaje final
            final_score_text = render_text(f"Pirámides: {piramides_correctas}/{total_piramides}", 30, (255, 255, 255))
            score_x = SCREEN_WIDTH // 2 - final_score_text.get_width() // 2
            screen.blit(final_score_text, (score_x, score_y))
            
            # Mostrar instrucciones para salir
            instruction_text = render_text("REGRESANDO AL MENU PRINCIPAL", 30, (218, 0, 167))
            instruction_x = SCREEN_WIDTH // 2 - instruction_text.get_width() // 2
            instruction_y = score_y + final_score_text.get_height() + 10
            screen.blit(instruction_text, (instruction_x, instruction_y))

    pygame.display.update()
# Variables para el temporizador
start_time = time.time()
timeout = 10  # 10 segundos

# Variable para controlar el bucle del juego
waiting_for_enter = True

while waiting_for_enter:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting_for_enter = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                waiting_for_enter = False
    
    # Comprobar el temporizador
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time > timeout:
        waiting_for_enter = False

    pygame.mixer.music.stop()

cap.release()
cv2.destroyAllWindows()
pygame.quit()