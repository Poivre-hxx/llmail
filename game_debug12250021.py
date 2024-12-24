import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 720, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Grid")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game variables
GRID_WIDTH, GRID_HEIGHT = 9, 6
CELL_SIZE = 60
ENEMY_RADIUS = 15
TOWER_SIZE = 20
GAME_DURATION = 120  # 2 minutes in seconds

# Game objects
class Enemy:
    def __init__(self, path):
        self.path = path
        self.position = list(path[0])
        self.health = 100
        self.speed = 0.02
        self.path_index = 0

    def move(self):
        target = self.path[self.path_index]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            self.path_index += 1
            if self.path_index >= len(self.path):
                return True
        else:
            self.position[0] += (dx / distance) * self.speed
            self.position[1] += (dy / distance) * self.speed
        return False

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.position[0] * CELL_SIZE + CELL_SIZE // 2),
                                         int(self.position[1] * CELL_SIZE + CELL_SIZE // 2)), ENEMY_RADIUS)

class Tower:
    def __init__(self, x, y):
        self.position = (x, y)
        self.damage = 30
        self.range = 2 * CELL_SIZE
        self.cooldown = 60
        self.cooldown_timer = 0

    def draw(self):
        center_x = self.position[0] * CELL_SIZE + CELL_SIZE // 2
        center_y = self.position[1] * CELL_SIZE + CELL_SIZE // 2
        points = [
            (center_x, center_y - TOWER_SIZE),
            (center_x - TOWER_SIZE, center_y + TOWER_SIZE),
            (center_x + TOWER_SIZE, center_y + TOWER_SIZE)
        ]
        pygame.draw.polygon(screen, BLUE, points)
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), self.range, 1)

    def attack(self, enemies):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return

        for enemy in enemies:
            dx = (enemy.position[0] + 0.5) * CELL_SIZE - (self.position[0] + 0.5) * CELL_SIZE
            dy = (enemy.position[1] + 0.5) * CELL_SIZE - (self.position[1] + 0.5) * CELL_SIZE
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.range:
                enemy.health -= self.damage
                self.cooldown_timer = self.cooldown
                break

# Game functions
def generate_path():
    path = [(0, 0)]
    current = [0, 0]
    
    while current != [GRID_WIDTH - 1, GRID_HEIGHT - 1]:
        if current[0] < GRID_WIDTH - 1 and random.choice([True, False]):
            current[0] += 1
        elif current[1] < GRID_HEIGHT - 1:
            current[1] += 1
        path.append(tuple(current))
    
    return path

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_path(path):
    for i in range(len(path) - 1):
        start = (path[i][0] * CELL_SIZE + CELL_SIZE // 2, path[i][1] * CELL_SIZE + CELL_SIZE // 2)
        end = (path[i+1][0] * CELL_SIZE + CELL_SIZE // 2, path[i+1][1] * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.line(screen, GREEN, start, end, 3)

def draw_start_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 48)
    title = font.render("Tower Defense Grid", True, WHITE)
    start = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT * 2 // 3))
    pygame.display.flip()

def draw_end_screen(win):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 48)
    if win:
        text = font.render("You Win!", True, GREEN)
    else:
        text = font.render("Game Over!", True, RED)
    restart = font.render("Press SPACE to Restart", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT * 2 // 3))
    pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    path = generate_path()
    enemies = []
    towers = []
    currency = 100
    enemy_count = 0
    enemies_passed = 0
    start_time = 0
    game_state = "start"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state in ["start", "end"]:
                        path = generate_path()
                        enemies = []
                        towers = []
                        currency = 100
                        enemy_count = 0
                        enemies_passed = 0
                        start_time = pygame.time.get_ticks()
                        game_state = "playing"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and game_state == "playing":
                x, y = event.pos
                grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                if (grid_x, grid_y) not in path and currency >= 50:
                    towers.append(Tower(grid_x, grid_y))
                    currency -= 50

        if game_state == "start":
            draw_start_screen()
        elif game_state == "playing":
            # Spawn enemies
            if random.random() < 0.01 and enemy_count < 50:
                enemies.append(Enemy(path))
                enemy_count += 1

            # Update enemies
            for enemy in enemies[:]:
                if enemy.move():
                    enemies.remove(enemy)
                    enemies_passed += 1
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    currency += 30

            # Update towers
            for tower in towers:
                tower.attack(enemies)

            # Draw everything
            screen.fill(BLACK)
            draw_grid()
            draw_path(path)
            for enemy in enemies:
                enemy.draw()
            for tower in towers:
                tower.draw()

            # Draw UI
            font = pygame.font.Font(None, 36)
            currency_text = font.render(f"Currency: {currency}", True, WHITE)
            screen.blit(currency_text, (10, 10))
            
            enemies_text = font.render(f"Enemies Passed: {enemies_passed}/10", True, WHITE)
            screen.blit(enemies_text, (10, 50))

            time_left = max(0, GAME_DURATION - (pygame.time.get_ticks() - start_time) // 1000)
            time_text = font.render(f"Time Left: {time_left}s", True, WHITE)
            screen.blit(time_text, (WIDTH - 200, 10))

            pygame.display.flip()

            # Check win/lose conditions
            if enemies_passed >= 10:
                game_state = "end"
            elif time_left <= 0:
                game_state = "end"
        elif game_state == "end":
            draw_end_screen(time_left > 0)

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
