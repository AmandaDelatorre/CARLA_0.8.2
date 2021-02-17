from carla.settings import CarlaSettings
from carla import image_converter
from carla.client import make_carla_client, VehicleControl
from carla.tcp import TCPConnectionError
import pygame
import carla
import numpy as np   # para calcular a magnitude
from pygame.locals import K_DOWN
from pygame.locals import K_LEFT
from pygame.locals import K_RIGHT
from pygame.locals import K_SPACE
from pygame.locals import K_UP
from pygame.locals import K_a
from pygame.locals import K_d
from pygame.locals import K_p
from pygame.locals import K_q
from pygame.locals import K_r
from pygame.locals import K_s
from pygame.locals import K_w

import os

print("")
print("Bem vindo ao script \"Aula de Sistemas Automotivos\"")
print("Execute o CarlaUE4.exe como servidor: CarlaUE4.exe -windowed -carla-server")
print("")
print("Criando arquivo de configuração...")
print("")

settings = CarlaSettings()

# Configurações do servidor:
settings.QualityLevel='Epic'                 # Qualidade do gráfico do UnrealEngine
settings.NumberOfVehicles = 2               # Número de veículos NPC
settings.NumberOfPedestrians = 3            # Número de pedestres NPC
settings.SynchronousMode = False            # O servidor roda em modo assíncrono (não espera o cliente)
settings.SendNonPlayerAgentsInfo = True     # O servidor envia dados dos agentes NPC (veículos, pedestres, luzes de tráfego e placas de limite de velocidade)
settings.WeatherId = 13                     # Configuração do clima (https://carla.readthedocs.io/en/stable/carla_settings/#weather-presets)

# Configuração dos sensores:
#https://carla.readthedocs.io/en/stable/cameras_and_sensors/#camera-scene-final
# CAMERA1 - camera realística, conta com tratamento de imagem para se parecer com uma camera real
camera1 = carla.sensor.Camera('Camera1', PostProcessing='SceneFinal')                            #criação do sensor camera
camera1.set(FOV=90.0)                                                                            #Field of View do sensor
camera1.set_image_size(500,500)                                                                  #Resolução da imagem
camera1.set_position(x=0.30, y=0, z=1.30)                                                        #Posição no veículo
camera1.set_rotation(pitch=0, yaw=0,roll=0)                                                      #Orientação do sensor
settings.add_sensor(camera1)                                                                     #Adiciona o sensor na configuração

# CAMERA 2 - Camera de visão semântica: https://carla.readthedocs.io/en/stable/cameras_and_sensors/#camera-semantic-segmentation
camera2 = carla.sensor.Camera('Camera2', PostProcessing='SemanticSegmentation') #criação do sensor camera
camera2.set(FOV=90.0) #Field of View do sensor
camera2.set_image_size(500,500) #Resolução da imagem
camera2.set_position(x=0.30, y=0, z=1.30) #Posição no veículo
camera2.set_rotation(pitch=0, yaw=0,roll=0) #Orientação do sensor
settings.add_sensor(camera2) #Adiciona o sensor na configuração

# CAMERA 3 - Camera de profundidade: https://carla.readthedocs.io/en/stable/cameras_and_sensors/#camera-depth-map
camera3 = carla.sensor.Camera('Camera3', PostProcessing='Deth') #criação do sensor camera
camera3.set(FOV=90.0) #Field of View do sensor
camera3.set_image_size(500,500) #Resolução da imagem
camera3.set_position(x=-0.30, y=0, z=1.60) #Posição no veículo
camera3.set_rotation(pitch=0, yaw=180,roll=0) #Orientação do sensor
settings.add_sensor(camera3) #Adiciona o sensor na configuração

#SENSOR LIDAR - https://carla.readthedocs.io/en/stable/cameras_and_sensors/#ray-cast-based-lidar   
lidar = carla.sensor.Lidar('Lidar32')  #Cria o sensor LIDAR
lidar.set_position(0, 0, 1.4) #Posição do sensor no veículo
lidar.set_rotation(0, 0, 0) #Orientação do veículo
lidar.set(   #Especificações do lidar
    Channels=32,
    Range=50,
    PointsPerSecond=100000,
    RotationFrequency=10,
    UpperFovLimit=10,
    LowerFovLimit=-30)
settings.add_sensor(lidar) #Adiciona o sensor na configuração
   
print("------------------------------")
print("Arquivo de configuração:\n ")
print(settings)
print("------------------------------")

while True:
    try:
        print("Conectando ao servidor...")
        with make_carla_client('localhost',2000) as client:
            
            print("Conectado com sucesso!")

            print("Fazendo upload da configuração...")
            scene = client.load_settings(settings)

            # O mapa possui posições (spots) pré-definidos. Se não indicar a posição, uma será escolhida aleatóriamente
            print("Iniciando um episódio no spot 0")
            client.start_episode(0)

            # Criando uma janela na biblioteca pygame para visualizar dados coletados (imagem das cameras, LIDAR, ultrassônico, velocidade, etc...)
            print("Criando janela para visualização de dados:")
            pygame.init()

            #WINDOW_WIDTH = 800
            #WINDOW_HEIGHT = 600
            #MINI_WINDOW_WIDTH = 320
            #MINI_WINDOW_HEIGHT = 180

            display = pygame.display.set_mode((1000,1000))

            # Iniciando loop para coleta e visualização de dados:
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True   
                
                # Coletando dados:
                measurements, sensor_data = client.read_data()

                # Measurements:
                # Apagando o texto anterior com um retângulo
                pygame.draw.rect(display, (160,95,155), pygame.Rect(0, 0, 1000, 70))                

                aceleracao = measurements.player_measurements.acceleration
                aceleracaox = float(aceleracao.x)
                aceleracaoz = float(aceleracao.z)
                aceleracaoy = float(aceleracao.y)
                aceleracao1 =np.array([aceleracaox,aceleracaoz,aceleracaoy])
                magnitude = np.linalg.norm(aceleracao1)
                texto = "Aceleração= {:.2f} m/s²".format(magnitude)
                fonte = pygame.font.SysFont("Arial", 28)
                white = (255,255,255)
                texto = fonte.render(texto, 1, white)
                display.blit(texto, (10, 10))

                velocidade = measurements.player_measurements.forward_speed
                velocidade = velocidade*3.6       
        
                texto = "Velocidade= {:.2f} km/h".format(velocidade)
                fonte = pygame.font.SysFont("Arial", 28)
                white = (255,255,255)
                texto = fonte.render(texto, 1, white)
                display.blit(texto, (10, 40))        

                # Sensor Data:
                imagem_camera1 = sensor_data.get("Camera1", None)
                if imagem_camera1 is not None:
                    array = image_converter.to_rgb_array(imagem_camera1)
                    surface = pygame.surfarray.make_surface(array.swapaxes(0,1))
                    display.blit(surface, (0,70))

                imagem_camera2 = sensor_data.get("Camera2", None)
                if imagem_camera2 is not None:
                    array = image_converter.labels_to_cityscapes_palette(imagem_camera2)
                    surface = pygame.surfarray.make_surface(array.swapaxes(0,1))
                    display.blit(surface, (500,70))

                imagem_camera3 = sensor_data.get("Camera3", None)
                if imagem_camera3 is not None:
                    array = image_converter.depth_to_logarithmic_grayscale(imagem_camera3)
                    surface = pygame.surfarray.make_surface(array.swapaxes(0,1))
                    display.blit(surface, (0,570))


                lidar_measurement = sensor_data.get('Lidar32', None)
                if lidar_measurement is not None:
                    lidar_data = np.array(lidar_measurement.data[:, :2])
                    lidar_data *= 2.0
                    lidar_data += 100.0
                    lidar_data = np.fabs(lidar_data)
                    lidar_data = lidar_data.astype(np.int32)
                    lidar_data = np.reshape(lidar_data, (-1, 2))
                    #draw lidar
                    lidar_img_size = (500, 500, 3)
                    lidar_img = np.zeros(lidar_img_size)
                    lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
                    surface = pygame.surfarray.make_surface(lidar_img)
                    display.blit(surface, (500, 570))

                # Enviando comando de autopiloto
                client.send_control(measurements.player_measurements.autopilot_control)

                # Atualizando a janela do pygame:
                pygame.display.flip()

            break

    except TCPConnectionError as error:
        print("Erro de conexão")

print("Fim do script")

