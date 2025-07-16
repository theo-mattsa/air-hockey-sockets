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
PADDLE_SPEED = 12

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cliente Pong")
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 40)
countdown_font = pygame.font.Font(None, 200)

def redraw_window(win, p1, p2, ball, winner, players_online, countdown_val, button, voted):
    win.fill(BLACK)

    if players_online < 2:
        text_surface = small_font.render("Aguardando oponente...", True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)
    elif countdown_val > 0:
        text_surface = countdown_font.render(str(countdown_val), True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)
    elif countdown_val == 0:
        text_surface = font.render("VAI!", True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)
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
        return

    paddle1 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    play_again_button = pygame.Rect(WIDTH/2 - 150, HEIGHT/2 + 20, 300, 60)
    
    voted_for_reset = False
    
    initial_state = n.send("get")
    if initial_state:
        p1_server, p2_server = initial_state["paddles"]
        paddle1.x, paddle1.y = p1_server.x, p1_server.y
        paddle2.x, paddle2.y = p2_server.x, p2_server.y

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
        
        redraw_window(screen, drawable_p1, drawable_p2, drawable_ball, winner, players_online, countdown - 1, play_again_button, voted_for_reset)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()