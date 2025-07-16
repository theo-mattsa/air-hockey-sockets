import socket
from _thread import *
import pickle
import pygame
import time

HOST = "0.0.0.0"
PORT = 5555
WIDTH, HEIGHT = 800, 500
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL = 1, 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
except socket.error as e:
    print(f"Erro ao ligar o servidor: {e}")
    exit()

s.listen(2)
print("Servidor iniciado! Esperando por 2 jogadores...")

game_state = {}
players_connected = 0
reset_votes = set()
ball_speed_x, ball_speed_y = 0, 0

def setup_game_state():
    global ball_speed_x, ball_speed_y
    paddle1 = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_speed_x, ball_speed_y = BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL
    game_state.update({
        "paddles": [paddle1, paddle2],
        "ball": ball,
        "winner": None,
        "game_started": False,
        "countdown": 4,
    })

def start_new_round():
    global reset_votes
    setup_game_state()
    reset_votes.clear()
    start_new_thread(countdown_thread, ())
    print("Nova rodada iniciada. Contagem regressiva...")

setup_game_state()

def game_logic_thread():
    global ball_speed_x, ball_speed_y
    clock = pygame.time.Clock()
    while True:
        if game_state.get("game_started") and game_state.get("winner") is None:
            game_state["ball"].x += ball_speed_x
            game_state["ball"].y += ball_speed_y
            if game_state["ball"].left <= 0 or game_state["ball"].right >= WIDTH:
                ball_speed_x *= -1
            if game_state["ball"].colliderect(game_state["paddles"][0]) and ball_speed_y > 0:
                ball_speed_y *= -1
            if game_state["ball"].colliderect(game_state["paddles"][1]) and ball_speed_y < 0:
                ball_speed_y *= -1
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
    global players_connected, reset_votes
    conn.send(pickle.dumps(player_id))
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
            conn.sendall(pickle.dumps(game_state))
        except (ConnectionResetError, EOFError):
            break
            
    print(f"Jogador {player_id + 1} desconectado.")
    players_connected -= 1
    if player_id in reset_votes:
        reset_votes.remove(player_id) 
    conn.close()

start_new_thread(game_logic_thread, ())

while True:
    conn, addr = s.accept()
    player_id = players_connected
    start_new_thread(client_thread, (conn, player_id))
    players_connected += 1
    print(f"Conexão recebida de {addr}. Jogador {player_id + 1}.")
    
    if players_connected == 2 and game_state.get("countdown") == 4:
        start_new_round()