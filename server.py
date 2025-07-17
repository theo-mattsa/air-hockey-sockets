import socket
from _thread import *
import pickle
import pygame
import time
import math
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("SERVER_IP")
PORT = int(os.getenv("SERVER_PORT"))
WIDTH, HEIGHT = 960, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL = 4, 4
SPEED_INCREASE_PER_FRAME = 0.001
MAX_SPEED = 12

def setup_game_state():
    """
    Inicializa as variáveis utilizadas no jogo.
    """
    global ball_speed_x, ball_speed_y
    paddle1 = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_speed_x, ball_speed_y = BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL
    
    game_state["paddles"] = [paddle1, paddle2]
    game_state["ball"]= ball
    game_state["winner"]= None
    game_state["game_started"]= False
    game_state["countdown"]= 4

def start_new_round():
    global reset_votes
    setup_game_state()
    reset_votes.clear()
    start_new_thread(countdown_thread, ())
    print("Nova rodada iniciada. Contagem regressiva...")

def game_logic_thread():
    global ball_speed_x, ball_speed_y
    clock = pygame.time.Clock()
    while True:
        if game_state.get("game_started") and game_state.get("winner") is None:
            
            # aumenta a velocidade no eixo y e x (respectivamente)
            current_speed_y = abs(ball_speed_y)
            if current_speed_y < MAX_SPEED:
                new_speed_y = current_speed_y + SPEED_INCREASE_PER_FRAME
                ball_speed_y = math.copysign(new_speed_y, ball_speed_y)
            
            current_speed_x = abs(ball_speed_x)
            if current_speed_x < MAX_SPEED:
                new_speed_x = current_speed_x + SPEED_INCREASE_PER_FRAME
                ball_speed_x = math.copysign(new_speed_x, ball_speed_x)
            
            # atualiza a posição da bola
            game_state["ball"].x += ball_speed_x
            game_state["ball"].y += ball_speed_y
            
            # verifica se é necessário mudar a direção no eixo x
            if game_state["ball"].left <= 0 or game_state["ball"].right >= WIDTH:
                ball_speed_x *= -1
            
            # verifica se é necessário mudar a direção no eixo y
            if game_state["ball"].colliderect(game_state["paddles"][0]) and ball_speed_y > 0:
                ball_speed_y *= -1
            if game_state["ball"].colliderect(game_state["paddles"][1]) and ball_speed_y < 0:
                ball_speed_y *= -1
            
            # verifica se houve vencedor
            if game_state["ball"].top <= 0:
                game_state["winner"] = "Jogador 1 Venceu!"
            if game_state["ball"].bottom >= HEIGHT:
                game_state["winner"] = "Jogador 2 Venceu!"
        
        clock.tick(60)

def countdown_thread():
    while game_state.get("countdown", 0) > 0:
        time.sleep(1)
        if game_state.get("countdown", 0) > 0:
             game_state["countdown"] -= 1
    game_state["game_started"] = True

def client_thread(conn, player_id):
    global players_connected, reset_votes, player_names
    conn.send(pickle.dumps(player_id)) # envia o id do jogador para o cliente
    
    try:
        player_name = pickle.loads(conn.recv(2048))
        player_names[player_id] = player_name
        print(f"Jogador {player_id + 1} definiu o nome como: {player_name}")

        if players_connected == 2 and player_names[0] and player_names[1] and game_state.get("countdown") == 4:
            start_new_round()

        game_state["players_online"] = players_connected
        game_state["player_names"] = player_names
        conn.sendall(pickle.dumps(game_state))

    except (EOFError, ConnectionResetError):
        print(f"Jogador {player_id + 1} desconectado prematuramente.")
        players_connected -= 1
        conn.close()
        return
            
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            if isinstance(data, str) and data == "reset":
                reset_votes.add(player_id)
                if len(reset_votes) == 2:
                    start_new_round()
            elif isinstance(data, str) and data == "get":
                pass
            else: 
                game_state["paddles"][player_id] = data
            
            game_state["players_online"] = players_connected
            game_state["player_names"] = player_names
            
            conn.sendall(pickle.dumps(game_state))
        except (ConnectionResetError, EOFError):
            break
            
    print(f"Jogador {player_id + 1} desconectado.")
    players_connected -= 1
    player_names[player_id] = ""
    if player_id in reset_votes:
        reset_votes.remove(player_id) 
    conn.close()

game_state = dict()
players_connected = 0
reset_votes = set()
ball_speed_x, ball_speed_y = 0, 0
player_names = list()

setup_game_state()
start_new_thread(game_logic_thread, ())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket com endereçamento IPv4 com protocolo TCP na camada de transporte
try:
    s.bind((HOST, PORT))
except socket.error as e:
    print(f"Erro ao ligar o servidor: {e}")
    exit()
s.listen(4) # tamanho máximo da fila de requisições: 4

print("Servidor iniciado! Esperando por jogadores...")

while True:
    conn_socket, client_addr = s.accept()
    player_id = players_connected
    start_new_thread(client_thread, (conn_socket, player_id))
    players_connected += 1
    print(f"Conexão recebida de {client_addr}. Jogador {player_id + 1}.")