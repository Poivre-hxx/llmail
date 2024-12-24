
import pygame
import random
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
GRID_ROWS = 6
GRID_COLS = 9
CELL_SIZE = WINDOW_WIDTH // GRID_COLS
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.state = "menu"
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.level = Level()
        self.start_time = pygame.time.get_ticks()

    def run(self):
        while True:
            try:
                if self.state == "menu":
                    self.menu()
                elif self.state == "play":
                    self.play()
                elif self.state == "pause":
                    self.pause()
                elif self.state == "game_over":
                    self.game_over()
            except Exception as e:
                print(f"An error occurred: {e}")
                pygame.quit()
                return

    def menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "play"

        self.screen.fill(WHITE)
        title = self.font.render("Tower Defense", True, BLACK)
        start = self.font.render("Press SPACE to start", True, BLACK)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//3))
        self.screen.blit(start, (WINDOW_WIDTH//2 - start.get_width()//2, WINDOW_HEIGHT//2))
        pygame.display.flip()

    def play(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.state = "pause"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right click
                    x, y = pygame.mouse.get_pos()
                    grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                    self.level.place_tower(grid_x, grid_y, self.player)

        self.level.update(self.player)
        self.check_game_over()

        self.screen.fill(WHITE)
        self.level.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()
        self.clock.tick(FPS)

    def pause(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.state = "play"

        pause_text = self.font.render("PAUSED", True, BLACK)
        self.screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2))
        pygame.display.flip()

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset_game()
                self.state = "play"

        self.screen.fill(WHITE)
        if self.level.enemies_passed >= 10:
            text = self.font.render("Game Over! Press R to restart", True, BLACK)
        else:
            text = self.font.render("Victory! Press R to play again", True, BLACK)
        self.screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2))
        pygame.display.flip()

    def check_game_over(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= 120000:  # 2 minutes
            self.state = "game_over"
        elif self.level.enemies_passed >= 10:
            self.state = "game_over"

    def draw_ui(self):
        currency_text = self.font.render(f"Currency: {self.player.currency}", True, BLACK)
        self.screen.blit(currency_text, (10, 10))
        enemies_text = self.font.render(f"Enemies Passed: {self.level.enemies_passed}/10", True, BLACK)
        self.screen.blit(enemies_text, (10, 50))
        time_left = max(0, 120 - (pygame.time.get_ticks() - self.start_time) // 1000)
        time_text = self.font.render(f"Time Left: {time_left}s", True, BLACK)
        self.screen.blit(time_text, (10, 90))

class Player:
    def __init__(self):
        self.currency = 100

    def can_afford(self, cost):
        return self.currency >= cost

    def spend(self, amount):
        self.currency -= amount

    def earn(self, amount):
        self.currency += amount

class Level:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.path = self.generate_path()
        self.towers = []
        self.enemies = deque()
        self.enemies_passed = 0
        self.spawn_timer = 0

    def generate_path(self):
        path = [(0, 0)]
        x, y = 0, 0
        while (x, y) != (GRID_COLS-1, GRID_ROWS-1):
            if x < GRID_COLS-1 and random.choice([True, False]):
                x += 1
            elif y < GRID_ROWS-1:
                y += 1
            path.append((x, y))
        for x, y in path:
            self.grid[y][x] = 1
        return path

    def place_tower(self, x, y, player):
        if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS and self.grid[y][x] == 0 and player.can_afford(50):
            self.towers.append(Tower(x, y))
            player.spend(50)
            self.grid[y][x] = 2

    def spawn_enemy(self):
        self.enemies.append(Enemy(self.path[0]))

    def update(self, player):
        # Update enemies
        for _ in range(len(self.enemies)):
            enemy = self.enemies.popleft()
            enemy.move(self.path)
            if enemy.reached_end(self.path[-1]):
                self.enemies_passed += 1
            elif enemy.health <= 0:
                player.earn(30)
            else:
                self.enemies.append(enemy)

        # Update towers
        for tower in self.towers:
            tower.update(self.enemies)

        # Spawn new enemies
        self.spawn_timer += 1
        if self.spawn_timer >= FPS:  # Spawn every second
            self.spawn_enemy()
            self.spawn_timer = 0

    def draw(self, screen):
        # Draw grid and path
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                color = WHITE if self.grid[y][x] == 0 else GREEN
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Draw towers
        for tower in self.towers:
            tower.draw(screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.attack_power = 30
        self.attack_radius = 2 * CELL_SIZE
        self.attack_cooldown = 30
        self.attack_timer = 0

    def update(self, enemies):
        self.attack_timer += 1
        if self.attack_timer >= self.attack_cooldown:
            for enemy in enemies:
                if self.in_range(enemy):
                    enemy.take_damage(self.attack_power)
                    self.attack_timer = 0
                    break

    def in_range(self, enemy):
        distance = math.hypot(self.x * CELL_SIZE - enemy.x, self.y * CELL_SIZE - enemy.y)
        return distance <= self.attack_radius

    def draw(self, screen):
        center_x = self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.polygon(screen, BLUE, [
            (center_x, center_y - CELL_SIZE // 2),
            (center_x - CELL_SIZE // 2, center_y + CELL_SIZE // 2),
            (center_x + CELL_SIZE // 2, center_y + CELL_SIZE // 2)
        ])

class Enemy:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.health = 100
        self.max_health = 100
        self.speed = 0.02

    def move(self, path):
        target_index = path.index((int(self.x), int(self.y))) + 1
        if target_index < len(path):
            target_x, target_y = path[target_index]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

    def take_damage(self, amount):
        self.health -= amount

    def reached_end(self, end_pos):
        return (int(self.x), int(self.y)) == end_pos

    def draw(self, screen):
        x = int(self.x * CELL_SIZE + CELL_SIZE // 2)
        y = int(self.y * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, RED, (x, y), CELL_SIZE // 3)
        
        # Health bar
        health_width = int((self.health / self.max_health) * CELL_SIZE)
        pygame.draw.rect(screen, GREEN, (x - CELL_SIZE//2, y - CELL_SIZE//2 - 5, health_width, 3))
        pygame.draw.rect(screen, RED, (x - CELL_SIZE//2 + health_width, y - CELL_SIZE//2 - 5, CELL_SIZE - health_width, 3))

if __name__ == "__main__":
    game = Game()
    game.run()
