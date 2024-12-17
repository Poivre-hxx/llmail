import pygame
import random
import sys

# Game constants
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
GRID_SIZE = 20
INITIAL_SPEED = 10

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.body = [(100, 100), (90, 100), (80, 100)]
        self.direction = 'right'
        self.next_direction = 'right'
    
    def move(self):
        # Update direction
        self.direction = self.next_direction
        
        head = self.body[0]
        if self.direction == 'up':
            new_head = (head[0], head[1] - GRID_SIZE)
        elif self.direction == 'down':
            new_head = (head[0], head[1] + GRID_SIZE)
        elif self.direction == 'left':
            new_head = (head[0] - GRID_SIZE, head[1])
        else:  # right
            new_head = (head[0] + GRID_SIZE, head[1])
        
        self.body.insert(0, new_head)
        self.body.pop()  # Remove tail unless growing
    
    def grow(self):
        # Don't remove tail in next move
        self.body.append(self.body[-1])
    
    def check_collision(self):
        head = self.body[0]
        return (head[0] < 0 or
                head[0] >= SCREEN_WIDTH or
                head[1] < 0 or
                head[1] >= SCREEN_HEIGHT or
                head in self.body[1:])

class Food:
    def __init__(self):
        self.position = None
        self.spawn()
    
    def spawn(self, snake_body=None):
        if snake_body is None:
            snake_body = []
            
        # Generate new position until it's not on snake
        while True:
            x = random.randint(0, (SCREEN_WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
            y = random.randint(0, (SCREEN_HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
            self.position = (x, y)
            
            if self.position not in snake_body:
                break

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('贪吃蛇')
        self.clock = pygame.time.Clock()
        
        self.reset_game()
    
    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_active = True
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not self.game_active:
                    self.reset_game()
                    return True
                    
                if not self.game_active:
                    continue
                    
                if event.key == pygame.K_UP and self.snake.direction != 'down':
                    self.snake.next_direction = 'up'
                elif event.key == pygame.K_DOWN and self.snake.direction != 'up':
                    self.snake.next_direction = 'down'
                elif event.key == pygame.K_LEFT and self.snake.direction != 'right':
                    self.snake.next_direction = 'left'
                elif event.key == pygame.K_RIGHT and self.snake.direction != 'left':
                    self.snake.next_direction = 'right'
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def update(self):
        if not self.game_active:
            return
            
        self.snake.move()
        
        # Check food collision
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.spawn(self.snake.body)
            self.score += 1
            # Increase speed every 5 points, but not faster than 5 ticks
            if self.score % 5 == 0 and self.speed > 5:
                self.speed -= 1
        
        # Check death
        if self.snake.check_collision():
            self.game_active = False
    
    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw snake
        for pos in self.snake.body:
            pygame.draw.rect(self.screen, (0, 100, 0), (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
        
        # Draw food
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (self.food.position[0], self.food.position[1], GRID_SIZE, GRID_SIZE))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'得分: {self.score}', True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over message
        if not self.game_active:
            game_over_font = pygame.font.Font(None, 48)
            game_over_text = game_over_font.render('游戏结束!', True, (255, 0, 0))
            restart_text = font.render('按 R 键重新开始', True, (0, 0, 0))
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.speed)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()