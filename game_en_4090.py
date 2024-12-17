import pygame
import random
import sys

# Game constants
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
GRID_SIZE = 20
SPEED = 10

class Snake:
    def __init__(self):
        self.body = [(100, 100), (90, 100), (80, 100)]
        self.direction = 'right'

    def move(self):
        head = self.body[0]
        if self.direction == 'up':
            new_head = (head[0], head[1] - GRID_SIZE)
        elif self.direction == 'down':
            new_head = (head[0], head[1] + GRID_SIZE)
        elif self.direction == 'left':
            new_head = (head[0] - GRID_SIZE, head[1])
        else:
            new_head = (head[0] + GRID_SIZE, head[1])

        self.body.insert(0, new_head)

    def grow(self):
        self.body.append(self.body[-1])

    def check_collision(self):
        if (self.body[0][0] < 0 or
                self.body[0][0] >= SCREEN_WIDTH or
                self.body[0][1] < 0 or
                self.body[0][1] >= SCREEN_HEIGHT or
                self.body[0] in self.body[1:]):
            return True

class Food:
    def __init__(self):
        self.position = (random.randint(0, SCREEN_WIDTH // GRID_SIZE) * GRID_SIZE,
                         random.randint(0, SCREEN_HEIGHT // GRID_SIZE) * GRID_SIZE)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Classic Snake')
        self.clock = pygame.time.Clock()

        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed = SPEED

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.snake.direction != 'down':
                        self.snake.direction = 'up'
                    elif event.key == pygame.K_DOWN and self.snake.direction != 'up':
                        self.snake.direction = 'down'
                    elif event.key == pygame.K_LEFT and self.snake.direction != 'right':
                        self.snake.direction = 'left'
                    elif event.key == pygame.K_RIGHT and self.snake.direction != 'left':
                        self.snake.direction = 'right'

            self.snake.move()

            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.score += 1
                if self.score % 5 == 0:
                    self.speed -= 1

            if self.snake.check_collision():
                break

            self.screen.fill((255, 255, 255))
            for pos in self.snake.body:
                pygame.draw.rect(self.screen, (0, 0, 0), (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(self.screen, (255, 0, 0), (self.food.position[0], self.food.position[1], GRID_SIZE, GRID_SIZE))
            font = pygame.font.Font(None, 36)
            text = font.render(f'Score: {self.score}', True, (0, 0, 0))
            self.screen.blit(text, (10, 10))

            pygame.display.flip()
            self.clock.tick(self.speed)

        self.game_over()

    def game_over(self):
        self.screen.fill((255, 255, 255))
        font = pygame.font.Font(None, 36)
        text = font.render(f'Game Over! Your score is {self.score}.', True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()