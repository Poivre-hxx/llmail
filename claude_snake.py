import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 720, 480
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Snake settings
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = (1, 0)
snake_growth = False

# Food settings
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

# Game settings
score = 0
high_score = 0
game_speed = 10
target_score = 50

# Font
font = pygame.font.Font(None, 36)

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(SCREEN, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(SCREEN, WHITE, (0, y), (WIDTH, y))

def draw_snake():
    for segment in snake:
        pygame.draw.rect(SCREEN, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_food():
    pygame.draw.circle(SCREEN, RED, (food[0] * GRID_SIZE + GRID_SIZE // 2, food[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2)

def move_snake():
    global snake, snake_growth, score, food, game_speed

    new_head = (snake[0][0] + snake_direction[0], snake[0][1] + snake_direction[1])
    snake.insert(0, new_head)

    # Check for collision with food
    if snake[0] == food:
        score += 1
        snake_growth = True
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
        # Increase game speed every 5 points
        if score % 5 == 0:
            game_speed += 1

    if not snake_growth:
        snake.pop()
    else:
        snake_growth = False

def check_collision():
    # Check for collision with walls
    if (snake[0][0] < 0 or snake[0][0] >= GRID_WIDTH or
        snake[0][1] < 0 or snake[0][1] >= GRID_HEIGHT):
        return True

    # Check for collision with self
    if snake[0] in snake[1:]:
        return True

    return False

def game_over():
    global high_score
    if score > high_score:
        high_score = score
    
    game_over_text = font.render("Game Over! Press SPACE to restart", True, WHITE)
    SCREEN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    reset_game()

def reset_game():
    global snake, snake_direction, food, score, game_speed
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (1, 0)
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    score = 0
    game_speed = 10

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != (0, 1):
                snake_direction = (0, -1)
            if event.key == pygame.K_DOWN and snake_direction != (0, -1):
                snake_direction = (0, 1)
            if event.key == pygame.K_LEFT and snake_direction != (1, 0):
                snake_direction = (-1, 0)
            if event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                snake_direction = (1, 0)

    move_snake()

    if check_collision():
        game_over()

    SCREEN.fill(BLACK)
    draw_grid()
    draw_snake()
    draw_food()

    # Display score and high score
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    SCREEN.blit(score_text, (10, 10))
    SCREEN.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(game_speed)

    # Check win condition
    if score >= target_score or len(snake) == GRID_WIDTH * GRID_HEIGHT:
        game_over()

pygame.quit()
