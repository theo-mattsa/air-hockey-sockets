import socket
from _thread import *
import pickle
import pygame

# Config do servidor
HOST = "localhost"
PORT = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
except socket.error as e:
    print(f"Erro ao iniciar o servidor: {e}")
    exit()

s.listen(2)
print("Servidor iniciado! Esperando por 2 jogadores para conectar...")

# Game state
WIDTH, HEIGHT = 800, 500
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL = 1, 1

paddle1 = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
paddles = [paddle1, paddle2]

ball = pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed_x, ball_speed_y = BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL

game_state = {
    "paddles": paddles,
    "ball": ball,
    "winner": None,
    "game_started": False
}
players_connected = 0


def game_logic_thread():
    global ball_speed_x, ball_speed_y
    clock = pygame.time.Clock()
    while True:
        if game_state["game_started"] and game_state["winner"] is None:
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

def client_thread(conn, player_id):
    conn.send(pickle.dumps(player_id))
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            if isinstance(data, str) and data == "get":
                pass
            else:
                game_state["paddles"][player_id] = data
            conn.sendall(pickle.dumps(game_state))
        except (ConnectionResetError, EOFError):
            print(f"Jogador {player_id + 1} perdeu a conexão.")
            break
    global players_connected
    players_connected -= 1
    conn.close()

# Loop principal do servidor
start_new_thread(game_logic_thread, ())

while True:
    conn, addr = s.accept()
    player_id = players_connected
    start_new_thread(client_thread, (conn, player_id))
    players_connected += 1
    print(f"Conexão recebida de {addr}. Este é o Jogador {player_id + 1}.")
    if players_connected == 2:
        print("Ambos os jogadores estão conectados. O jogo vai começar!")
        game_state["game_started"] = True