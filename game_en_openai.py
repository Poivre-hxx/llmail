import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
GRID_SIZE = 20  # Each cell in the grid will be 20x20 pixels
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Classic Snake Game")

# Clock
clock = pygame.time.Clock()

# Snake class to manage snake behavior
class Snake:
    def __init__(self):
        self.body = [(5, 5), (5, 4), (5, 3)]  # Starting snake body
        self.direction = RIGHT
        self.growing = False
    
    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        if self.growing:
            self.body.insert(0, new_head)
            self.growing = False
        else:
            self.body = [new_head] + self.body[:-1]
    
    def grow(self):
        self.growing = True
    
    def collision_with_wall(self):
        head_x, head_y = self.body[0]
        return head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT
    
    def collision_with_self(self):
        head = self.body[0]
        return head in self.body[1:]
    
    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Food class to manage food behavior
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Game loop
def game_loop():
    snake = Snake()
    food = Food()
    score = 0
    speed = 10
    running = True
    game_over = False
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT

        if not game_over:
            snake.move()

            if snake.collision_with_wall() or snake.collision_with_self():
                game_over = True

            # Check if snake eats food
            if snake.body[0] == food.position:
                score += 1
                snake.grow()
                food.randomize_position()
                # Increase speed every 5 food eaten
                if score % 5 == 0:
                    speed += 1

            # Draw everything
            snake.draw(screen)
            food.draw(screen)

            # Display score
            font = pygame.font.SysFont('Arial', 20)
            score_text = font.render(f'Score: {score}', True, WHITE)
            screen.blit(score_text, (10, 10))

            pygame.display.update()

            clock.tick(speed)

        else:
            # Game over screen
            font = pygame.font.SysFont('Arial', 40)
            game_over_text = font.render(f'Game Over! Final Score: {score}', True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
            pygame.display.update()

            pygame.time.wait(2000)  # Wait 2 seconds before quitting the game
            running = False

# Start the game
game_loop()
pygame.quit()
