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
pygame.display.set_caption("Cliente Pong")

# Configuração dos tamanhos das fontes
font = pygame.font.Font(size=74)
small_font = pygame.font.Font(size=40)
input_font = pygame.font.Font(size=50) 
countdown_font = pygame.font.Font(size=200)

def draw_name_input_screen(win, text, input_box, ok_button, is_active):
    win.fill(BLACK)
    
    # Renderiza o prompt de instrução
    prompt_surface = input_font.render("Digite seu nome:", True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH/2, HEIGHT/2 - 80))
    win.blit(source=prompt_surface, 
             dest=prompt_rect)

    color = COLOR_ACTIVE if is_active else COLOR_INACTIVE
    pygame.draw.rect(win, color, input_box, 2)
    
    # Renderiza o texto digitado pelo usuário
    text_surface = input_font.render(text, True, WHITE)
    win.blit(
        source=text_surface, 
        dest=(input_box.x + 10, input_box.y + 10)
    )
    
    # Desenha o botão OK
    pygame.draw.rect(
        surface=win, 
        color=GREEN_BTN, 
        rect=ok_button
    )
    ok_text_surface = small_font.render("OK", True, WHITE)
    ok_text_rect = ok_text_surface.get_rect(
        center=ok_button.center
    )
    win.blit(
        source=ok_text_surface, 
        dest=ok_text_rect
    )

    pygame.display.flip()

def draw_waiting_screen(win):
    win.fill(BLACK)
    text_surface = small_font.render("Aguardando oponente...", True, WHITE)
    text_rect = text_surface.get_rect(
        center=(WIDTH / 2, HEIGHT / 2)
    )
    win.blit(
        source=text_surface,
        dest=text_rect
    )
    pygame.display.flip()

def draw_counting_screen(win, countdown_val, opponent_name):
    win.fill(BLACK)
    opponent_surface = small_font.render(f"Seu oponente é: {opponent_name}", True, WHITE)
    opponent_rect = opponent_surface.get_rect(
        center=(WIDTH / 2, HEIGHT / 2 + 150)
    )
    win.blit(
        source=opponent_surface,
        dest=opponent_rect
    )

    countdown_surface = countdown_font.render(str(countdown_val), True, WHITE)
    countdown_rect = countdown_surface.get_rect(
        center=(WIDTH / 2, HEIGHT / 2)
    )
    win.blit(
        source=countdown_surface,
        dest=countdown_rect
    )
    pygame.display.flip()

def redraw_window(win, p1, p2, ball, winner, players_online, countdown_val, button, voted, opponent_name):
    win.fill(BLACK)

    if players_online < 2:
        text_surface = small_font.render("Aguardando oponente...", True, WHITE)
        text_rect = text_surface.get_rect(
            center=(WIDTH / 2, HEIGHT / 2)
        )
        win.blit(
            source=text_surface,
            dest=text_rect
        )

    elif countdown_val > 0:
        opponent_surface = small_font.render(f"Seu oponente é: {opponent_name}", True, WHITE)
        opponent_rect = opponent_surface.get_rect(
            center=(WIDTH / 2, HEIGHT / 2 + 150)
        )
        win.blit(
            source=opponent_surface,
            dest=opponent_rect
        )

        countdown_surface = countdown_font.render(str(countdown_val), True, WHITE)
        countdown_rect = countdown_surface.get_rect(
            center=(WIDTH / 2, HEIGHT / 2)
        )
        win.blit(
            source=countdown_surface,
            dest=countdown_rect
        )

    elif countdown_val == 0:
        go_surface = font.render("VAI!", True, WHITE)
        go_rect = go_surface.get_rect(
            center=(WIDTH / 2, HEIGHT / 2)
        )
        win.blit(
            source=go_surface,
            dest=go_rect
        )

    else:
        pygame.draw.rect(
            surface=win,
            color=BLUE,
            rect=p1
        )
        pygame.draw.rect(
            surface=win,
            color=RED,
            rect=p2
        )
        pygame.draw.ellipse(
            surface=win,
            color=WHITE,
            rect=ball
        )

    if winner:
        winner_surface = font.render(winner, True, WHITE)
        winner_rect = winner_surface.get_rect(
            center=(WIDTH / 2, HEIGHT / 2 - 50)
        )
        win.blit(
            source=winner_surface,
            dest=winner_rect
        )

        button_color = (150, 150, 0) if voted else (0, 150, 0)
        pygame.draw.rect(
            surface=win,
            color=button_color,
            rect=button
        )

        button_text = "Aguardando..." if voted else "Iniciar novo jogo"
        button_surface = small_font.render(button_text, True, WHITE)
        button_rect = button_surface.get_rect(
            center=button.center
        )
        win.blit(
            source=button_surface,
            dest=button_rect
        )

    pygame.display.flip()

def get_winner_text(winner, player_id):
    if winner == "Jogador 1 Venceu!":
        return "Você ganhou!" if player_id == 0 else "Você perdeu!"
    elif winner == "Jogador 2 Venceu!":
        return "Você perdeu!" if player_id == 0 else "Você ganhou!"
    return winner

def main():
    running = True
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        load_dotenv()
        server_ip = os.getenv("SERVER_IP")
        server_port = int(os.getenv("SERVER_PORT"))
        client_socket.connect((server_ip, server_port))
        print(f"Conectado ao servidor: {server_ip}:{server_port}")
    except socket.error as e:
        print(f"Erro de conexão: {e}")
        return
        
    player_id = pickle.loads(client_socket.recv(2048))
    print(f"ID do jogador: {player_id}")

    player_name = ""
    input_box = pygame.Rect(WIDTH/2 - 200, HEIGHT/2 - 25, 400, 50)
    ok_button = pygame.Rect(WIDTH/2 - 75, HEIGHT/2 + 50, 150, 60)
    active = False
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

                if ok_button.collidepoint(event.pos) and player_name:
                    name_entered = True

            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and player_name:
                    name_entered = True
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if input_font.size(player_name + event.unicode)[0] < input_box.width - 20:
                        player_name += event.unicode
        
        draw_name_input_screen(screen, player_name, input_box, ok_button, active)

    pygame.display.set_caption(f"Pong - {player_name}")
    client_socket.send(pickle.dumps(player_name))
    
    # Receber estado inicial
    initial_state = pickle.loads(client_socket.recv(4096))
    paddle1 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    play_again_button = pygame.Rect(WIDTH/2 - 150, HEIGHT/2 + 20, 300, 60)
    voted_for_reset = False
    
    if initial_state:
        paddle1.x, paddle1.y = initial_state["paddles"][0].x, initial_state["paddles"][0].y
        paddle2.x, paddle2.y = initial_state["paddles"][1].x, initial_state["paddles"][1].y
    else: 
        print("Erro: Estado inicial inválido")
        running = False

    my_paddle = paddle1 if player_id == 0 else paddle2
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        
        try:
            # Enviar estado da raquete
            client_socket.send(pickle.dumps(my_paddle))
            
            # Receber estado do jogo
            game_state = pickle.loads(client_socket.recv(4096))
            if not game_state:
                print("Conexão com servidor perdida")
                running = False
                break
            
            # Processar estado
            countdown = game_state.get("countdown", -1)
            player_names = game_state.get("player_names", ["", ""])
            opponent_name = player_names[1 - player_id]
            p1_server = game_state["paddles"][0]
            p2_server = game_state["paddles"][1]
            ball_server = game_state["ball"]
            winner = game_state["winner"]
            players_online = game_state.get("connected_players", 0)  # Campo corrigido

            # Verificar se o jogo terminou
            if winner:
                winner_text = get_winner_text(winner, player_id)
            else:
                winner_text = None
                voted_for_reset = False

            # Preparar elementos visuais
            drawable_p1 = p1_server.copy()
            drawable_p2 = p2_server.copy()
            drawable_ball = ball_server.copy()
            
            # Tratamento de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if winner_text and not voted_for_reset and play_again_button.collidepoint(event.pos):
                        client_socket.send(pickle.dumps("play again"))
                        voted_for_reset = True
            
            # Movimento da raquete
            if not winner_text and countdown < 1:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and my_paddle.left > 0:
                    my_paddle.x -= PADDLE_SPEED
                if keys[pygame.K_RIGHT] and my_paddle.right < WIDTH:
                    my_paddle.x += PADDLE_SPEED
            
            # Renderização
            redraw_window(
                screen, 
                drawable_p1, 
                drawable_p2, 
                drawable_ball, 
                winner_text, 
                players_online, 
                countdown,  # Sem subtração
                play_again_button, 
                voted_for_reset, 
                opponent_name
            )
                
        except (ConnectionResetError, EOFError) as e:
            print(f"Erro de conexão: {e}")
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()