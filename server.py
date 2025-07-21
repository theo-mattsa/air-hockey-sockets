import socket
import threading
import pickle
import pygame
import time
import math
from dotenv import load_dotenv
import os
from random import randint
import time

WIDTH, HEIGHT = 960, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL = 4, 4
SPEED_INCREASE_PER_FRAME = 0.005
MAX_SPEED = 12

# Inicializar pygame para usar Rect
pygame.init()

class Game:
    """
    Representa um jogo de Pong com dois jogadores.
    Cada jogo tem seu próprio lock para acessar o estado do jogo de forma segura.
    """
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.lock = threading.Lock() 
        self.state = {
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
    
    def get_state_copy(self):
        """Pega uma cópia segura do estado atual do jogo"""
        with self.lock:
            return self.state.copy()
    
    def update_connected_players(self, delta: int):
        """Atualiza o número de jogadores conectados de forma segura"""
        with self.lock:
            self.state["connected_players"] += delta
    
    def set_player_name(self, player_id: int, name: str):
        """Define o nome de um jogador de forma segura"""
        with self.lock:
            self.state["player_names"][player_id] = name
    
    def update_paddle(self, player_id: int, paddle_rect):
        """Atualiza a posição da raquete de um jogador"""
        with self.lock:
            self.state["paddles"][player_id] = paddle_rect
    
    def increment_play_again_votes(self):
        """Adiciona um voto para jogar novamente"""
        with self.lock:
            self.state["play_again_votes"] += 1
            return self.state["play_again_votes"]
    
    def reset_game(self):
        """Reinicia o jogo para uma nova partida"""
        with self.lock:
            self.state["paddles"] = [
                pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, HEIGHT - 20 - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT),
                pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
            ]
            self.state["ball"] = pygame.Rect(WIDTH/2 - BALL_RADIUS, HEIGHT/2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
            self.state["winner_id"] = None
            self.state["game_started"] = False
            self.state["countdown"] = 3
            self.state["ball_speed"] = [BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL]
            self.state["play_again_votes"] = 0
    
    def set_player_left(self):
        """Marca que um jogador saiu da partida"""
        with self.lock:
            self.state["player_leaved"] = True
    
    def deactivate(self):
        """Desativa o jogo (encerra a partida)"""
        with self.lock:
            self.state["active"] = False

def countdown_thread(game: Game):
    """
    Faz a contagem regressiva antes do jogo começar
    """
    print(f"Iniciando countdown para jogo {game.game_id}")
    
    while True:
        with game.lock:
            is_active = game.state["active"]
            current_countdown = game.state["countdown"]
        if not is_active:
            break
        if current_countdown > 0:
            time.sleep(1)
            with game.lock:
                game.state["countdown"] -= 1
                print(f"Jogo {game.game_id}: Countdown = {game.state['countdown']+1}")
        else:
            with game.lock:
                game.state["game_started"] = True
            break
    
    print(f"Countdown do jogo {game.game_id} finalizado")

def game_logic_thread(game: Game):
    """
    Controla o movimento da bola e verifica quem ganhou.
    """
    print(f"Iniciando lógica do jogo {game.game_id}")

    while True:
        # Leitura rápida do estado com lock mínimo
        with game.lock:
            is_active = game.state["active"]
            countdown = game.state["countdown"]
            winner_id = game.state["winner_id"]
        
        # Verifica se deve continuar
        if not is_active:
            break

        # Só processa física se jogo está rodando
        if countdown <= 0 and winner_id is None:
            
            # Captura snapshot do estado atual com lock mínimo
            with game.lock:
                current_ball = game.state["ball"].copy()
                current_speed = game.state["ball_speed"].copy()
                current_paddles = [paddle.copy() for paddle in game.state["paddles"]]
                connected_players = game.state["connected_players"]
            
            ball_speed_x, ball_speed_y = current_speed
            
            # Aumenta velocidade gradualmente
            if abs(ball_speed_y) < MAX_SPEED:
                new_speed_y = abs(ball_speed_y) + SPEED_INCREASE_PER_FRAME
                ball_speed_y = math.copysign(new_speed_y, ball_speed_y)
            
            if abs(ball_speed_x) < MAX_SPEED:
                new_speed_x = abs(ball_speed_x) + SPEED_INCREASE_PER_FRAME
                ball_speed_x = math.copysign(new_speed_x, ball_speed_x)
            
            # Calcula nova posição da bola
            new_ball_x = current_ball.x + ball_speed_x
            new_ball_y = current_ball.y + ball_speed_y
            
            # Colisões com paredes laterais
            if new_ball_x <= 0 or new_ball_x >= WIDTH - current_ball.width:
                ball_speed_x *= -1
                new_ball_x = current_ball.x + ball_speed_x  # Recalcula posição
            
            # Cria rect temporário para teste de colisão
            temp_ball = pygame.Rect(new_ball_x, new_ball_y, current_ball.width, current_ball.height)
            
            # Colisões com raquetes
            if (temp_ball.colliderect(current_paddles[0]) and ball_speed_y > 0):
                ball_speed_y = -abs(ball_speed_y)
                new_ball_y = current_ball.y + ball_speed_y
            elif (temp_ball.colliderect(current_paddles[1]) and ball_speed_y < 0):
                ball_speed_y = abs(ball_speed_y)
                new_ball_y = current_ball.y + ball_speed_y
            
            # Verifica condições de vitória
            new_winner_id = None
            if new_ball_y <= 0:
                new_winner_id = 0
            elif new_ball_y >= HEIGHT - current_ball.height:
                new_winner_id = 1
            
            #  Aplicação dos resultados com lock mínimo
            with game.lock:
                game.state["ball"].x = new_ball_x
                game.state["ball"].y = new_ball_y
                game.state["ball_speed"] = [ball_speed_x, ball_speed_y]
                
                if new_winner_id is not None:
                    game.state["winner_id"] = new_winner_id
                    if connected_players == 2:
                        print(f'Jogo {game.game_id}: Jogador {new_winner_id+1} venceu!')
        
        time.sleep(1/60)  # 60 quadros por segundo
    print(f"Encerrando lógica do jogo {game.game_id}")

def client_thread(conn: socket.socket, game: Game, player_id: int):
    """
    Thread que cuida da comunicação com um cliente específico.
    """
    try:
        print(f"Cliente conectado: Jogo {game.game_id}, Jogador {player_id+1}")
        
        # Manda qual jogador ele é (0 ou 1)
        conn.send(pickle.dumps(player_id))
        
        # Recebe o nome que o jogador digitou
        try:
            player_name = pickle.loads(conn.recv(2048))
        except Exception as e:
            print(f"Erro ao receber nome: {e}")
            player_name = "Fulano"
        
        if player_name == "\0testando\0":
            print("Requisição de teste.")
            game.deactivate()
            while True:
                data = conn.recv(2048)
                if not data: # Cliente desconectou
                    break
                time.sleep(0.01) # Simulação da execução da lógica
                try:
                    conn.send(pickle.dumps("testando"))
                except BrokenPipeError: # Socket cliente encerrado
                    break
        else:
            # Salva o nome do jogador no jogo
            game.set_player_name(player_id, player_name)
            print(f"Jogador {player_id+1} do jogo {game.game_id} definido como: {player_name}")

            # Aumenta o contador de jogadores conectados
            game.update_connected_players(1)
            
            # Se ambos jogadores estão conectados, inicia countdown
            with game.lock:
                if game.state["connected_players"] == 2 and not game.state["game_started"]:
                    countdown_logic = threading.Thread(target=countdown_thread, args=(game,))
                    countdown_logic.start()
                    game.state["game_started"] = True
            
            # Loop principal do cliente
            while game.state["active"]:
                try:
                    # Manda o estado atual do jogo para o cliente
                    conn.send(pickle.dumps(game.get_state_copy()))
                    
                    data = conn.recv(2048)
                    if not data: # Cliente desconectou
                        break
                    
                    received_data = pickle.loads(data)
                    
                    if isinstance(received_data, str) and received_data == "play_again":
                        votes = game.increment_play_again_votes()
                        print(f"Voto para reiniciar jogo {game.game_id}: {votes}/2")
                        
                        # Se ambos votaram, reinicia o jogo
                        if votes >= 2:
                            print(f"Reiniciando jogo {game.game_id}")
                            game.reset_game()
                            countdown_logic = threading.Thread(target=countdown_thread, args=(game,))
                            countdown_logic.start()
                            
                    elif isinstance(received_data, pygame.Rect):
                        # Atualiza onde está a raquete do jogador
                        game.update_paddle(player_id, received_data)
                    
                except Exception as e:
                    print(f"Erro na comunicação com {player_name}: {e}")
                    break
            
            print(f"Desconectando {player_name} do jogo {game.game_id}")
            game.update_connected_players(-1)
            game.set_player_left()
            
            # Verifica se deve desativar o jogo
            with game.lock:
                if game.state["connected_players"] == 0:
                    game.deactivate()
                    print(f"Jogo {game.game_id} encerrado - sem jogadores")
    except Exception as e:
        print(f"Erro na thread do cliente {player_name} do jogo {game.game_id}: {e}")
    
    try:
        conn.close()
    except:
        pass

def main():
    load_dotenv()
    
    # Configurações do servidor
    ip_address = os.getenv("SERVER_IP")
    port_number = int(os.getenv("SERVER_PORT"))
    
    # TCP socket para o servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    try:
        s.bind((ip_address, port_number))
        s.listen(5) 
        print(f"Servidor Pong iniciado em {ip_address}:{port_number}")
        print("Aguardando conexões...")
    except socket.error as e:
        print(f"Erro ao iniciar servidor: {e}")
        return
    
    # Lista de jogos esperando o segundo jogador
    unmatched_games = list()  
    
    try:
        while True:
            conn, addr = s.accept()
            print(f"Nova conexão de {addr}")
            
            game = None
            player_id = int()

            # Procura se tem algum jogo esperando jogador, senão cria um novo
            if len(unmatched_games) > 0:
                game = unmatched_games.pop()
                player_id = 1
                print(f"Adicionando jogador ao jogo {game.game_id}")
            else:
                # Cria um jogo novo
                game_id = str(randint(1000, 9999))
                game = Game(game_id)
                unmatched_games.append(game)
                player_id = 0
                print(f"Criando novo jogo {game.game_id}")
                
                # Começa a lógica do jogo (movimento da bola)
                game_logic = threading.Thread(target=game_logic_thread, args=(game,))
                game_logic.start()
            
            # Inicia thread do cliente
            client_logic = threading.Thread(target=client_thread, args=(conn, game, player_id))
            client_logic.start()
            
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo usuário")
    except Exception as e:
        print(f"Erro no servidor: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()