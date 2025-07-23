import pygame
import sys
from dotenv import load_dotenv
import os
import socket
import pickle

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 960, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN_BTN = (0, 180, 0)
PADDLE_SPEED = 12
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cliente Air Hockey")

# Fontes
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 40)
input_font = pygame.font.Font(None, 50)
countdown_font = pygame.font.Font(None, 200)

def draw_name_input_screen(win, text, input_box, ok_button, is_active):
    """Desenha a tela de entrada de nome"""
    win.fill(BLACK)
    
    # Prompt
    prompt_surface = input_font.render("Digite seu nome:", True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH/2, HEIGHT/2 - 80))
    win.blit(prompt_surface, prompt_rect)
    
    # Input box
    color = COLOR_ACTIVE if is_active else COLOR_INACTIVE
    pygame.draw.rect(win, color, input_box, 2)
    
    # Texto digitado
    text_surface = input_font.render(text, True, WHITE)
    win.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    
    # Botão OK
    pygame.draw.rect(win, GREEN_BTN, ok_button, border_radius=10)
    ok_text = small_font.render("OK", True, WHITE)
    ok_rect = ok_text.get_rect(center=ok_button.center)
    win.blit(ok_text, ok_rect)
    
    pygame.display.flip()

def redraw_window(win, p1, p2, ball, winner, players_online, countdown_val, button, voted, opponent_name, no_opponent, player_id):
    """Desenha o estado atual do jogo"""
    win.fill(BLACK)
    
    # Jogo inativo por falta de oponente
    if no_opponent:
        text = small_font.render("Seu oponente se desconectou. Inicie outra sessão.", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        win.blit(text, text_rect)
    
    # Aguardando jogadores
    elif players_online < 2:
        text = small_font.render("Aguardando oponente...", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        win.blit(text, text_rect)
    
    # Countdown
    elif countdown_val > 0:
        # Nome do oponente
        if opponent_name:
            opponent_text = small_font.render(f"Oponente: {opponent_name}", True, WHITE)
            opponent_rect = opponent_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 150))
            win.blit(opponent_text, opponent_rect)
        
        # Countdown
        countdown_text = countdown_font.render(str(countdown_val), True, WHITE)
        countdown_rect = countdown_text.get_rect(center=(WIDTH/2, HEIGHT/2))
        win.blit(countdown_text, countdown_rect)
    
    # Jogo iniciado
    elif countdown_val == 0 and not winner:
        # Cada jogador vê seu paddle embaixo
        if player_id == 0:
            # Jogador 0 - Seu paddle (p1) embaixo em azul
            pygame.draw.rect(win, BLUE, p1)
            # O oponente (p2) em cima em vermelho
            pygame.draw.rect(win, RED, p2)
            pygame.draw.ellipse(win, WHITE, ball)
        else:
            # Inverte a visualização para o jogador 1
            my_paddle_inverted = pygame.Rect(p2.x, HEIGHT - 20 - PADDLE_HEIGHT, p2.width, p2.height)
            opponent_paddle_inverted = pygame.Rect(p1.x, 20, p1.width, p1.height)
            ball_inverted = pygame.Rect(ball.x, HEIGHT - ball.y - ball.height, ball.width, ball.height)   
            
            pygame.draw.rect(win, RED, my_paddle_inverted)
            pygame.draw.rect(win, BLUE, opponent_paddle_inverted)
            pygame.draw.ellipse(win, WHITE, ball_inverted)
    
    # Tela de vitória
    if winner and not no_opponent:
        winner_text = font.render(winner, True, WHITE)
        winner_rect = winner_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        win.blit(winner_text, winner_rect)
        
        # Botão de reiniciar
        button_color = (150, 150, 0) if voted else (0, 150, 0)
        pygame.draw.rect(win, button_color, button, border_radius=10)
        
        button_text = "Aguardando..." if voted else "Revanche"
        button_surface = small_font.render(button_text, True, WHITE)
        button_rect = button_surface.get_rect(center=button.center)
        win.blit(button_surface, button_rect)
    
    pygame.display.flip()

def get_winner_text(winner_id:int, player_id:int):
    """
    Retorna "Você perdeu!" se o jogador perdeu, "Você ganhou!" se o jogador ganhou ou 
    None se ainda não houver um vencedor.
    """
    if winner_id == None:
        return None
    elif winner_id == player_id:
        return "Você ganhou!"
    else:
        return "Você perdeu!"

def main():
    # Configuração de conexão
    load_dotenv()
    ip_address = os.getenv("SERVER_IP")
    port_number = int(os.getenv("SERVER_PORT"))

    # TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((ip_address, port_number))
        print(f"Conectado ao servidor {ip_address}:{port_number}")
    except Exception as e:
        print(f"Erro de conexão: {e}")
        pygame.quit()
        sys.exit()
    
    # Recebe ID do jogador
    try:
        player_id = pickle.loads(client_socket.recv(2048))
        print(f"Sou o jogador {player_id+1}")
    except Exception as e:
        print(f"Erro ao receber ID: {e}")
        pygame.quit()
        sys.exit()
    
    # Entrada de nome
    player_name = ""
    input_box = pygame.Rect(WIDTH/2 - 200, HEIGHT/2 - 25, 400, 50)
    ok_button = pygame.Rect(WIDTH/2 - 75, HEIGHT/2 + 50, 150, 60)
    active = True
    name_entered = False
    
    while not name_entered:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                
                if ok_button.collidepoint(event.pos) and player_name.strip():
                    name_entered = True
            
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and player_name.strip():
                    name_entered = True
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 15 and event.unicode.isprintable():
                        player_name += event.unicode
        
        draw_name_input_screen(screen, player_name, input_box, ok_button, active)
    
    # Envia nome para o servidor
    try:
        client_socket.send(pickle.dumps(player_name))
        print(f"Nome enviado: {player_name}")
    except Exception as e:
        print(f"Erro ao enviar nome: {e}")
        pygame.quit()
        sys.exit()
    
    pygame.display.set_caption(f"Air hockey - {player_name}")
    
    # Inicialização das raquetes
    my_paddle = pygame.Rect(WIDTH/2 - PADDLE_WIDTH/2, 
                           HEIGHT - 30 if player_id == 0 else 20, 
                           PADDLE_WIDTH, PADDLE_HEIGHT)
    
    play_again_button = pygame.Rect(WIDTH/2 - 100, HEIGHT/2 + 50, 200, 60)
    voted_for_reset = False
    clock = pygame.time.Clock()
    running = True
    
    print("Entrando no loop principal...")
    winner_text = None
    while running:
        clock.tick(60)
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if winner_text is not None and event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos) and not voted_for_reset:
                    try:
                        client_socket.send(pickle.dumps("play_again"))
                        voted_for_reset = True
                        print("Voto para reiniciar enviado")
                        continue
                    except Exception as e:
                        print(f"Erro ao enviar voto: {e}")
            
        # Controle dos paddles
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and my_paddle.left > 0:
            my_paddle.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and my_paddle.right < WIDTH:
            my_paddle.x += PADDLE_SPEED
        
        try:
            # Envia posição da raquete
            client_socket.send(pickle.dumps(my_paddle))
            
            # Recebe estado do jogo
            data = client_socket.recv(4096)
            if not data:
                print("Estado do jogo vazio - desconectando")
                break
            
            game_state = pickle.loads(data)
            
            # Extrai informações do estado
            p1_server = game_state.get("paddles")[0]
            p2_server = game_state.get("paddles")[1]
            ball_server = game_state.get("ball")
            winner_id = game_state.get("winner_id")
            players_online = game_state.get("connected_players")
            countdown = game_state.get("countdown")
            player_names = game_state.get("player_names")
            no_opponent = game_state.get("player_leaved")

            # Nome do oponente
            opponent_name = player_names[1 - player_id]
            
            # Reset do voto se jogo reiniciou
            if winner_id == None:
                voted_for_reset = False
            
            # Texto de vitória ou derrota personalizado
            winner_text = get_winner_text(winner_id, player_id)
            
            # Renderização
            redraw_window(screen, p1_server, p2_server, ball_server, 
                         winner_text, players_online, countdown, 
                         play_again_button, voted_for_reset, opponent_name, no_opponent, player_id)
            
        except (ConnectionResetError, EOFError, socket.error) as e:
            print(f"Erro de conexão: {e}")
            break
        except Exception as e:
            print(f"Erro geral: {e}")
            break
    
    print("Encerrando cliente...")
    client_socket.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()