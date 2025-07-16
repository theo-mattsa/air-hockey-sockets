import pygame
import sys
from network import Network

# Config inicial do Pygame
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 500
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PADDLE_SPEED = 7

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 30)


def redraw_window(win, p1, p2, ball, winner_text, waiting_text):
    """Função para desenhar todos os elementos na tela."""
    win.fill(BLACK)
    
    # Desenha os paddles e a bola
    pygame.draw.rect(win, BLUE, p1)
    pygame.draw.rect(win, RED, p2)
    pygame.draw.ellipse(win, WHITE, ball)
    
    if waiting_text:
        text_surface = small_font.render(waiting_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        win.blit(text_surface, text_rect)
    if winner_text:
        text_surface = font.render(winner_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20))
        win.blit(text_surface, text_rect)
    pygame.display.flip()


def main():
    running = True
    n = Network()
    player_id = n.get_player_id()
    if player_id is None:
        print("Não foi possível obter o ID do jogador. Encerrando o programa...")
        return
    print(f"Conectado! Você é o jogador {player_id + 1}")
    paddle1 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(0, 0, BALL_RADIUS * 2, BALL_RADIUS * 2)

    # Obtendo o estado inicial do jogo do servidor
    initial_state = n.send("get")
    
    # Atualizando paddles e bola com o estado inicial do servidor
    if initial_state:
        p1_server, p2_server = initial_state["paddles"]
        paddle1.x, paddle1.y = p1_server.x, p1_server.y
        paddle2.x, paddle2.y = p2_server.x, p2_server.y

    # Obtem o paddle do correto do jogador
    my_paddle = paddle1 if player_id == 0 else paddle2
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        # Envia o paddle atualizado para o servidor e recebe o estado do jogo
        game_state = n.send(my_paddle)
        if not game_state:
            running = False
            print("Perda de conexão com o servidor.")
            break
        
        p1_server, p2_server = game_state["paddles"]
        paddle1.x, paddle1.y = p1_server.x, p1_server.y
        paddle2.x, paddle2.y = p2_server.x, p2_server.y
        
        ball_server = game_state["ball"]
        ball.x, ball.y = ball_server.x, ball_server.y

        winner = game_state["winner"]
        game_started = game_state["game_started"]
        
        waiting_msg = ""
        if not game_started and not winner:
            waiting_msg = "Esperando o segundo jogador conectar..."

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not winner:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and my_paddle.left > 0:
                my_paddle.x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT] and my_paddle.right < WIDTH:
                my_paddle.x += PADDLE_SPEED

        redraw_window(screen, paddle1, paddle2, ball, winner, waiting_msg)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()