import socket
import threading
import pickle
import pygame
import time
import math
from dotenv import load_dotenv
import os
from random import randint


WIDTH, HEIGHT = 960, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL = 4, 4
SPEED_INCREASE_PER_FRAME = 0.001
MAX_SPEED = 12

lock = threading.Lock()

# Inicializar pygame para usar Rect
pygame.init()

def setup_game_state() -> tuple[dict, str]:
    """
    Retornando um dict com o estado inicial do jogo e um id para o jogo (respectivamente).
    """
    
    game_state = {
        "paddles": [
            pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT),
            pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
        ],
        "ball": pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2),
        "winner_id": None,
        "game_started": False,
        "countdown": 3,
        "ball_speed": [BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL],
        "player_names": ["", ""],
        "connected_players": 0,
        "active": True,
        "play_again_votes": 0,
        "player_leaved": False
    }
    
    game_id = str(randint(1000, 9999))
    return game_state, game_id

def game_logic_thread(game_id:str, game_state:dict):
    """
    Implementa a lógica de movimentação da bola (verificando os casos de vitória/derrota) 
    para o jogo cujo id é fornecido enquanto esse estiver ativo. 
    """

    print(f"Iniciando lógica do jogo {game_id}")

    while game_state["active"]:

        # Verifica se a contagem regressiva finalizou e se não há vencedor 
        if game_state["countdown"] <= 0 and game_state["winner_id"] is None:
            ball_speed_x, ball_speed_y = game_state["ball_speed"]
            
            # Aumenta velocidade gradualmente
            if abs(ball_speed_y) < MAX_SPEED:
                new_speed_y = abs(ball_speed_y) + SPEED_INCREASE_PER_FRAME
                ball_speed_y = math.copysign(new_speed_y, ball_speed_y)
            
            if abs(ball_speed_x) < MAX_SPEED:
                new_speed_x = abs(ball_speed_x) + SPEED_INCREASE_PER_FRAME
                ball_speed_x = math.copysign(new_speed_x, ball_speed_x)
            
            # Atualiza posição da bola
            game_state["ball"].x += ball_speed_x
            game_state["ball"].y += ball_speed_y
            
            # Colisões com paredes laterais
            if game_state["ball"].left <= 0 or game_state["ball"].right >= WIDTH:
                ball_speed_x *= -1
            
            # Colisões com raquetes
            if (game_state["ball"].colliderect(game_state["paddles"][0]) and ball_speed_y > 0):
                ball_speed_y = -abs(ball_speed_y)
            if (game_state["ball"].colliderect(game_state["paddles"][1]) and ball_speed_y < 0):
                ball_speed_y = abs(ball_speed_y)
            
            # Atualiza velocidade
            game_state["ball_speed"] = [ball_speed_x, ball_speed_y]
            
            # Verifica condições de vitória
            if game_state["ball"].top <= 0:
                game_state["winner_id"] = 0
            elif game_state["ball"].bottom >= HEIGHT:
                game_state["winner_id"] = 1 
            
            if game_state["winner_id"] is not None and game_state["connected_players"] == 2:
                print(f'Jogo {game_id}: Jogador {game_state["winner_id"]+1} venceu!')
        
        time.sleep(1/60)  # 60 FPS
    
    print(f"Encerrando lógica do jogo {game_id}")

def countdown_thread(game_id:str, game_state:dict):
    """Thread para contagem regressiva"""
    print(f"Iniciando countdown para jogo {game_id}")
    
    while game_state["active"]: 
        if game_state["countdown"] > 0:
            time.sleep(1)
            game_state["countdown"] -= 1
            print(f"Jogo {game_id}: Countdown = {game_state['countdown']+1}")
        else:
            game_state["game_started"] = True
            break
    
    print(f"Countdown do jogo {game_id} finalizado")

def client_thread(conn:socket.socket, game_id:str, player_id:int, game_state:dict):
    """
    Gerencia cliente individual
    """
    global lock
    try:
        print(f"Cliente conectado: Jogo {game_id}, Jogador {player_id+1}")
        
        # Envia ID do jogador
        conn.send(pickle.dumps(player_id))
        
        # Recebe nome do jogador
        try:
            player_name = pickle.loads(conn.recv(2048))
        except Exception as e:
            print(f"Erro ao receber nome: {e}")
            player_name = "Fulano"
        game_state["player_names"][player_id] = player_name
        print(f"Jogador {player_id+1} do jogo {game_id} definido como: {player_name}")

        lock.acquire()  
        game_state["connected_players"] += 1
        lock.release()
        
        # Se ambos jogadores estão conectados, inicia countdown
        lock.acquire()
        if game_state["connected_players"] == 2 and not game_state["game_started"]:
            countdown_logic = threading.Thread(target=countdown_thread, args=(game_id, game_state))
            countdown_logic.start()
            game_state["game_started"] = True
        lock.release()
        
        # Loop principal do cliente
        while game_state["active"]:
            try:
                # Envia estado atual
                conn.send(pickle.dumps(game_state))
                
                data = conn.recv(2048)
                if not data: # Conexão fechada pelo cliente
                    break
                
                received_data = pickle.loads(data)
                
                if isinstance(received_data, str) and received_data == "play_again":
                    lock.acquire()
                    game_state["play_again_votes"] += 1
                    lock.release()

                    print(f"Voto para reiniciar jogo {game_id}: {game_state['play_again_votes']}/2")
                    
                    # Se ambos votaram, reinicia o jogo
                    lock.acquire()
                    if game_state["play_again_votes"] >= 2:
                        print(f"Reiniciando jogo {game_id}")
                        game_state["paddles"] = [
                            pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT),
                            pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
                        ]
                        game_state["ball"] = pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
                        game_state["winner_id"] = None
                        game_state["game_started"] = False
                        game_state["countdown"] = 3
                        game_state["ball_speed"] = [BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL]
                        game_state["play_again_votes"] = 0
                        countdown_logic = threading.Thread(target=countdown_thread, args=(game_id, game_state))
                        countdown_logic.start()
                    lock.release()
                elif isinstance(received_data, pygame.Rect):
                    # Atualiza posição da raquete
                    lock.acquire()
                    game_state["paddles"][player_id] = received_data
                    lock.release()
                
            except Exception as e:
                print(f"Erro na comunicação com {player_name}: {e}")
                break
        
    except Exception as e:
        print(f"Erro na thread do cliente {player_name} do jogo {game_id}: {e}")
    
    finally:
        print(f"Desconectando {player_name} do jogo {game_id}")
        lock.acquire()
        game_state["connected_players"] -= 1
        game_state["player_leaved"] = True
        if game_state["connected_players"] == 0:
            game_state["active"] = False
            print(f"Jogo {game_id} encerrado - sem jogadores")
        lock.release()
        try:
            conn.close()
        except:
            pass

def main():
    load_dotenv()
    ip_address = os.getenv("SERVER_IP")
    port_number = int(os.getenv("SERVER_PORT"))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4 com TCP na camada de transporte
    
    try:
        s.bind((ip_address, port_number))
        s.listen(5) # fila de no máximo 5 requisições pendentes
        print(f"Servidor Pong iniciado em {ip_address}:{port_number}")
        print("Aguardando conexões...")
    except socket.error as e:
        print(f"Erro ao iniciar servidor: {e}")
        return
    
    # Estruturas de controle
    unmatched_games = list()
    
    try:
        while True:
            conn, addr = s.accept()
            print(f"Nova conexão de {addr}")
            
            game_id = str()
            player_id = int()
            game_state = dict()

            # Procura jogo disponível ou cria novo
            if len(unmatched_games) > 0:
                game_id, game_state = unmatched_games.pop()
                player_id = 1
                print(f"Adicionando jogador ao jogo {game_id}")
            else:
                game_state, game_id = setup_game_state()
                unmatched_games.append((game_id, game_state))
                player_id = 0
                print(f"Criando novo jogo {game_id}")
                
                # Inicia thread de lógica do jogo
                game_logic = threading.Thread(target=game_logic_thread, args=(game_id, game_state))
                game_logic.start()
            
            # Inicia thread do cliente
            client_logic = threading.Thread(target=client_thread, args=(conn, game_id, player_id, game_state))
            client_logic.start()
            
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo usuário")
    except Exception as e:
        print(f"Erro no servidor: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()