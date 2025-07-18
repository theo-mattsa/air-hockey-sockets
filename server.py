import socket
from _thread import *
import pickle
import pygame
import time
import math
from dotenv import load_dotenv
import os
from random import randint

load_dotenv()

IP = os.getenv("SERVER_IP")
PORT = int(os.getenv("SERVER_PORT"))
WIDTH, HEIGHT = 960, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL = 4, 4
SPEED_INCREASE_PER_FRAME = 0.001
MAX_SPEED = 12

def setup_game_state() -> tuple[dict, str]:
    """
    Inicializa as variáveis utilizadas no jogo e retorna um id válido para o novo jogo.
    """
    game_state = dict()
    game_state["paddles"] = [pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT),
                             pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)]
    game_state["ball"] = pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    game_state["winner"] = None
    game_state["game_started"] = False
    game_state["countdown"] = 4
    game_state["ball_speed"] = [BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL]
    game_state["player_names"] = ["", ""]
    game_state["connected_players"] = 0
    game_state["active"] = True

    game_id = str(randint(0, 10000))
    return game_state, game_id

def game_logic_thread(game_id: str, active_games: dict):
    """
    Lógica principal do jogo para uma partida específica
    """
    game_state = active_games[game_id]
    clock = pygame.time.Clock()
    
    while game_state["active"]:
        if game_state.get("game_started") and game_state.get("winner") is None:
            ball_speed_x, ball_speed_y = game_state["ball_speed"]
            
            # Aumenta a velocidade gradualmente
            current_speed_y = abs(ball_speed_y)
            if current_speed_y < MAX_SPEED:
                new_speed_y = current_speed_y + SPEED_INCREASE_PER_FRAME
                ball_speed_y = math.copysign(new_speed_y, ball_speed_y)
            
            current_speed_x = abs(ball_speed_x)
            if current_speed_x < MAX_SPEED:
                new_speed_x = current_speed_x + SPEED_INCREASE_PER_FRAME
                ball_speed_x = math.copysign(new_speed_x, ball_speed_x)
            
            # Atualiza a posição da bola
            game_state["ball"].x += ball_speed_x
            game_state["ball"].y += ball_speed_y
            
            # Colisões com as paredes
            if game_state["ball"].left <= 0 or game_state["ball"].right >= WIDTH:
                ball_speed_x *= -1
            
            # Colisões com as raquetes
            if game_state["ball"].colliderect(game_state["paddles"][0]) and ball_speed_y > 0:
                ball_speed_y *= -1
            if game_state["ball"].colliderect(game_state["paddles"][1]) and ball_speed_y < 0:
                ball_speed_y *= -1
            
            # Atualiza velocidade no estado
            game_state["ball_speed"] = [ball_speed_x, ball_speed_y]
            
            # Verifica vitória
            if game_state["ball"].top <= 0:
                game_state["winner"] = "Jogador 1 Venceu!"
            if game_state["ball"].bottom >= HEIGHT:
                game_state["winner"] = "Jogador 2 Venceu!"
        
        clock.tick(60)
    
    # Remove o jogo quando inativo
    if game_id in active_games:
        del active_games[game_id]

def countdown_thread(game_id: str, active_games: dict):
    """
    Contagem regressiva para iniciar uma partida
    """
    game_state = active_games[game_id]
    while game_state["countdown"] > 0 and game_state["active"]:
        time.sleep(1)
        if game_state["countdown"] > 0:
            game_state["countdown"] -= 1
    
    if game_state["active"]:
        game_state["game_started"] = True

def client_thread(conn: socket.socket, game_id: str, player_id: int, active_games: dict, unmatched_games: dict):
    """
    Gerencia a conexão com um cliente específico
    """
    try:
        game_state = active_games[game_id]
        game_state["connected_players"] += 1
        
        # Envia ID do jogador
        conn.send(pickle.dumps(player_id))
        
        # Recebe nome do jogador
        player_name = pickle.loads(conn.recv(2048))
        game_state["player_names"][player_id] = player_name
        print(f"Jogador {player_id} ({player_name}) conectado ao jogo {game_id}")

        # Inicia contagem regressiva se ambos estiverem conectados
        if (game_state["player_names"][0] and game_state["player_names"][1] and 
            game_state["countdown"] == 4 and game_id in unmatched_games):
            start_new_thread(countdown_thread, (game_id, active_games))
            unmatched_games.pop(game_id, None)  # Remove da lista de espera

        while game_state["active"]:
            # Envia estado do jogo
            conn.sendall(pickle.dumps(game_state))
            
            # Recebe dados do cliente
            data = conn.recv(2048)
            if not data:
                break
                
            data = pickle.loads(data)
            
            if data == "play again":
                # Solicitação para jogar novamente
                print(f"Jogador {player_name} solicitou novo jogo")
                game_state["connected_players"] -= 1
                if game_state["connected_players"] == 0:
                    game_state["active"] = False
                
                # Encontra ou cria novo jogo
                new_game_id = None
                if unmatched_games:
                    new_game_id = next(iter(unmatched_games))
                    new_player_id = 1
                else:
                    new_game_state, new_game_id = setup_game_state()
                    active_games[new_game_id] = new_game_state
                    unmatched_games[new_game_id] = True
                    new_player_id = 0
                    start_new_thread(game_logic_thread, (new_game_id, active_games))
                
                # Redireciona cliente
                start_new_thread(client_thread, (conn, new_game_id, new_player_id, active_games, unmatched_games))
                return
            else:
                # Atualiza posição do paddle
                game_state["paddles"][player_id] = data
    
    except (ConnectionResetError, EOFError, socket.error) as e:
        print(f"Erro na conexão: {e}")
    
    finally:
        # Desconexão do cliente
        print(f"Jogador {player_name} desconectado do jogo {game_id}")
        game_state["connected_players"] -= 1
        conn.close()
        
        # Remove jogo se não houver jogadores
        if game_state["connected_players"] == 0:
            game_state["active"] = False
            unmatched_games.pop(game_id, None)

# Configuração do servidor
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((IP, PORT))
except socket.error as e:
    print(f"Erro ao ligar o servidor: {e}")
    exit()

s.listen()
print(f"Servidor iniciado em {IP}:{PORT}! Esperando por jogadores...")

# Estruturas para gerenciar jogos
active_games = {}  # Todos os jogos ativos
unmatched_games = {}  # Jogos aguardando segundo jogador

while True:
    conn, addr = s.accept()
    print(f"Nova conexão de {addr}")

    # Encontra ou cria um jogo
    if unmatched_games:
        game_id = next(iter(unmatched_games))
        player_id = 1
    else:
        game_state, game_id = setup_game_state()
        active_games[game_id] = game_state
        unmatched_games[game_id] = True
        player_id = 0
        start_new_thread(game_logic_thread, (game_id, active_games))

    # Inicia thread para o cliente
    start_new_thread(client_thread, (conn, game_id, player_id, active_games, unmatched_games))