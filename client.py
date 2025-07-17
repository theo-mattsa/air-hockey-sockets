import pygame
import sys
from network import Network

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

# Fontes
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 40)
input_font = pygame.font.Font(None, 50) 
countdown_font = pygame.font.Font(None, 200)

def draw_name_input_screen(win, text, input_box, ok_button, is_active):
    win.fill(BLACK)
    
    prompt_surface = input_font.render("Digite seu nome:", True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH/2, HEIGHT/2 - 80))
    win.blit(prompt_surface, prompt_rect)

    color = COLOR_ACTIVE if is_active else COLOR_INACTIVE
    pygame.draw.rect(win, color, input_box, 2)
    
    text_surface = input_font.render(text, True, WHITE)
    win.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    
    pygame.draw.rect(win, GREEN_BTN, ok_button)
    ok_text_surface = small_font.render("OK", True, WHITE)
    ok_text_rect = ok_text_surface.get_rect(center=ok_button.center)
    win.blit(ok_text_surface, ok_text_rect)

    pygame.display.flip()

def redraw_window(win, p1, p2, ball, winner, players_online, countdown_val, button, voted, opponent_name):
    win.fill(BLACK)

    #  Aguardando o segundo jogador se conectar.
    if players_online < 2:
        text_surface = small_font.render("Aguardando oponente...", True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)

    # Contagem regressiva para iniciar a rodada.
    elif countdown_val > 0:
        opponent_text = f"Seu oponente é: {opponent_name}"
        opponent_surface = small_font.render(opponent_text, True, WHITE)
        opponent_rect = opponent_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 150))
        win.blit(opponent_surface, opponent_rect)
        
        text_surface = countdown_font.render(str(countdown_val), True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)

    # Sinal de início 
    elif countdown_val == 0:
        text_surface = font.render("VAI!", True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)

    # Jogo em andamento.
    else:
        pygame.draw.rect(win, BLUE, p1)
        pygame.draw.rect(win, RED, p2)
        pygame.draw.ellipse(win, WHITE, ball)

    if winner:
        winner_surface = font.render(winner, True, WHITE)
        winner_rect = winner_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        win.blit(winner_surface, winner_rect)
        
        button_color = (150, 150, 0) if voted else (0, 150, 0)
        pygame.draw.rect(win, button_color, button)
        button_text = "Aguardando..." if voted else "Iniciar novo jogo"
        button_surface = small_font.render(button_text, True, WHITE)
        button_rect = button_surface.get_rect(center=button.center)
        win.blit(button_surface, button_rect)
        
    pygame.display.flip()

def get_winner_text(winner, player_id):
    if winner == "Jogador 1 Venceu!":
        return "Você ganhou!" if player_id == 0 else "Você perdeu!"
    elif winner == "Jogador 2 Venceu!":
        return "Você perdeu!" if player_id == 0 else "Você ganhou!"
    return winner

def main():
    running = True
    n = Network()
    player_id = n.get_player_id()
    if player_id is None:
        print("Não foi possível conectar ao servidor.")
        return

    player_name = ''
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
                if ok_button.collidepoint(event.pos):
                    if player_name:
                        name_entered = True

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if player_name:
                            name_entered = True
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if input_font.size(player_name)[0] < input_box.width - 20:
                            player_name += event.unicode
        
        draw_name_input_screen(screen, player_name, input_box, ok_button, active)

    pygame.display.set_caption(f"Cliente Pong - {player_name}")
    initial_state = n.send(player_name)
    
    paddle1 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    play_again_button = pygame.Rect(WIDTH/2 - 150, HEIGHT/2 + 20, 300, 60)
    
    voted_for_reset = False
    
    if initial_state:
        p1_server, p2_server = initial_state["paddles"]
        paddle1.x, paddle1.y = p1_server.x, p1_server.y
        paddle2.x, paddle2.y = p2_server.x, p2_server.y
    else: 
        print("Não foi possível obter o estado inicial do jogo.")
        running = False

    my_paddle = paddle1 if player_id == 0 else paddle2
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        
        game_state = n.send(my_paddle)
        if not game_state:
            running = False
            break
        
        p1_server = game_state["paddles"][0]
        p2_server = game_state["paddles"][1]
        ball_server = game_state["ball"]
        winner = game_state["winner"]
        countdown = game_state.get("countdown", -1)
        players_online = game_state.get("players_online", 0)
        
        player_names = game_state.get("player_names", ["", ""])
        opponent_id = 1 - player_id
        opponent_name = player_names[opponent_id]

        if not winner:
            voted_for_reset = False

        drawable_p1 = p1_server.copy()
        drawable_p2 = p2_server.copy()
        drawable_ball = ball_server.copy()

        if player_id == 1:
            drawable_p1.y = HEIGHT - p1_server.y - PADDLE_HEIGHT
            drawable_p2.y = HEIGHT - p2_server.y - PADDLE_HEIGHT
            drawable_ball.y = HEIGHT - ball_server.y - (BALL_RADIUS * 2)
        
        winner = get_winner_text(winner, player_id) if winner else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if winner and not voted_for_reset and play_again_button.collidepoint(event.pos):
                    n.send("reset")
                    voted_for_reset = True
        
        if not winner and countdown < 1:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and my_paddle.left > 0:
                my_paddle.x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT] and my_paddle.right < WIDTH:
                my_paddle.x += PADDLE_SPEED
        
        redraw_window(screen, drawable_p1, drawable_p2, drawable_ball, winner, players_online, countdown - 1, play_again_button, voted_for_reset, opponent_name)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()