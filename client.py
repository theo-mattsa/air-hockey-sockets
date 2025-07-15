import pygame
import sys


pygame.init()

WIDTH, HEIGHT = 800, 500
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10
BALL_RADIUS = 8
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PADDLE_SPEED = 7
BALL_SPEED_X_INITIAL = 4
BALL_SPEED_Y_INITIAL = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Rects para deteção de colisão e posicionamento dos objetos
paddle1 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT) 
paddle2 = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT) 
ball = pygame.Rect(0, 0, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed_x, ball_speed_y = 0, 0

game_over = True
winner_text = ""

# Font para exibir mensagens
font = pygame.font.Font(None, 50) 

def reset_game():
    global ball_speed_x, ball_speed_y, game_over, winner_text
    
    # Centraliza os paddles e a bola
    paddle1.centerx = WIDTH / 2
    paddle1.bottom = HEIGHT - 5 
    
    paddle2.centerx = WIDTH / 2
    paddle2.top = 5
    
    ball.centerx = WIDTH / 2
    ball.centery = HEIGHT / 2
    
    ball_speed_x = BALL_SPEED_X_INITIAL
    ball_speed_y = BALL_SPEED_Y_INITIAL
    
    game_over = False
    winner_text = ""

# Inicia o jogo
reset_game()
game_over = True 

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # <--- NOVO: Reinicia o jogo ao pressionar qualquer tecla se o jogo acabou
        if event.type == pygame.KEYDOWN and game_over:
            reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        
        # Controles do Jogador 1
        if keys[pygame.K_LEFT] and paddle1.left > 0:
            paddle1.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle1.right < WIDTH:
            paddle1.x += PADDLE_SPEED
        
        # Controles do Jogador 2
        if keys[pygame.K_a] and paddle2.left > 0:
            paddle2.x -= PADDLE_SPEED
        if keys[pygame.K_d] and paddle2.right < WIDTH:
            paddle2.x += PADDLE_SPEED

        # Movimento da Bola
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Colisão da Bola com as paredes laterais
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speed_x *= -1
            
        # Colisão da Bola com os paddles
        if ball.colliderect(paddle1) and ball_speed_y > 0:
            ball_speed_y *= -1
        if ball.colliderect(paddle2) and ball_speed_y < 0:
            ball_speed_y *= -1
            
        # Fim de Jogo 
        if ball.top <= 0:
            winner_text = "Jogador 1 Venceu!"
            game_over = True
        if ball.bottom >= HEIGHT:
            winner_text = "Jogador 2 Venceu!"
            game_over = True



    screen.fill(BLACK)
    
    # Desenha os paddles
    pygame.draw.rect(screen, BLUE, paddle1)
    pygame.draw.rect(screen, RED, paddle2)
    
    # Desenha a bola
    pygame.draw.ellipse(screen, WHITE, ball)
    
 
    if game_over:
        if winner_text: 
            text_surface = font.render(winner_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30))
            screen.blit(text_surface, text_rect)
        else: 
            start_font = pygame.font.Font(None, 30)
            start_surface = start_font.render("Pressione qualquer tecla para começar", True, WHITE)
            start_rect = start_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            screen.blit(start_surface, start_rect)

    pygame.display.flip()
    
    # Limita a taxa de quadros
    clock.tick(30)


pygame.quit()
sys.exit()