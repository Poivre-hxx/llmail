
import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 384
CELL_SIZE = 64
GRID_WIDTH = 9
GRID_HEIGHT = 6

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# Game objects
class GameObject:
    def __init__(self, id, type, position):
        self.id = id
        self.type = type
        self.position = position
        self.components = {}

class Monster(GameObject):
    def __init__(self, id, position, health, speed):
        super().__init__(id, "monster", position)
        self.components["health"] = Health(health)
        self.components["movement"] = Movement(speed)
        self.components["render"] = Render("Circle", RED)

class Tower(GameObject):
    def __init__(self, id, position, attack_power, attack_radius):
        super().__init__(id, "tower", position)
        self.components["attack"] = Attack(attack_power, attack_radius)
        self.components["render"] = Render("Triangle", BLUE)

# Components
class Health:
    def __init__(self, max_health):
        self.max_health = max_health
        self.current_health = max_health

    def take_damage(self, amount):
        self.current_health -= amount
        return self.current_health <= 0

class Movement:
    def __init__(self, speed):
        self.speed = speed

    def update(self, game_object, path):
        current_pos = game_object.position
        target_index = 0
        for i, pos in enumerate(path):
            if pos[0] > current_pos[0] or pos[1] > current_pos[1]:
                target_index = i
                break
        target_pos = path[target_index]
        
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            game_object.position[0] += dx * self.speed
            game_object.position[1] += dy * self.speed

class Attack:
    def __init__(self, attack_power, attack_radius):
        self.attack_power = attack_power
        self.attack_radius = attack_radius
        self.cooldown = 0

    def update(self, game_object, monsters, dt):
        self.cooldown -= dt
        if self.cooldown <= 0:
            for monster in monsters:
                distance = math.sqrt((game_object.position[0] - monster.position[0])**2 + 
                                     (game_object.position[1] - monster.position[1])**2)
                if distance <= self.attack_radius:
                    if monster.components["health"].take_damage(self.attack_power):
                        monsters.remove(monster)
                        return True  # Monster killed
                    self.cooldown = 1  # Set cooldown to 1 second
                    break
        return False

class Render:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color

    def draw(self, game_object, screen):
        x, y = game_object.position
        if self.shape == "Circle":
            pygame.draw.circle(screen, self.color, (int(x), int(y)), 20)
        elif self.shape == "Triangle":
            points = [
                (x, y - 20),
                (x - 17, y + 10),
                (x + 17, y + 10)
            ]
            pygame.draw.polygon(screen, self.color, points)

# Game manager
class GameManager:
    def __init__(self):
        self.currency = 100
        self.towers = []
        self.monsters = []
        self.path = self.generate_path()
        self.wave_number = 0
        self.monsters_escaped = 0
        self.max_monsters_escaped = 10
        self.survival_time = 120
        self.time_elapsed = 0

    def generate_path(self):
        path = [(0, 0)]
        current = [0, 0]
        while current != [GRID_WIDTH-1, GRID_HEIGHT-1]:
            if current[0] < GRID_WIDTH-1 and random.choice([True, False]):
                current[0] += 1
            elif current[1] < GRID_HEIGHT-1:
                current[1] += 1
            else:
                current[0] += 1
            path.append(tuple(current))
        return [(x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2) for x, y in path]

    def update(self, dt):
        self.time_elapsed += dt

        # Update monsters
        for monster in self.monsters[:]:
            monster.components["movement"].update(monster, self.path)
            if monster.position[0] >= SCREEN_WIDTH-CELL_SIZE//2 and monster.position[1] >= SCREEN_HEIGHT-CELL_SIZE//2:
                self.monsters.remove(monster)
                self.monsters_escaped += 1

        # Update towers
        for tower in self.towers:
            if tower.components["attack"].update(tower, self.monsters, dt):
                self.currency += 30  # Reward for killing a monster

        # Spawn new wave
        if len(self.monsters) == 0:
            self.spawn_wave()

    def spawn_wave(self):
        self.wave_number += 1
        for _ in range(5 + self.wave_number):
            monster = Monster(f"monster_{len(self.monsters)}", list(self.path[0]), 100, 1)
            self.monsters.append(monster)

    def place_tower(self, position):
        grid_pos = (position[0] // CELL_SIZE, position[1] // CELL_SIZE)
        if self.currency >= 50 and grid_pos not in [(x//CELL_SIZE, y//CELL_SIZE) for x, y in self.path]:
            tower = Tower(f"tower_{len(self.towers)}", position, 30, CELL_SIZE*2)
            self.towers.append(tower)
            self.currency -= 50
            return True
        return False

    def check_game_over(self):
        if self.monsters_escaped >= self.max_monsters_escaped:
            return "lose"
        if self.time_elapsed >= self.survival_time:
            return "win"
        return None

# Main game loop
def main():
    clock = pygame.time.Clock()
    game_manager = GameManager()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    grid_pos = (mouse_pos[0] // CELL_SIZE * CELL_SIZE + CELL_SIZE // 2,
                                mouse_pos[1] // CELL_SIZE * CELL_SIZE + CELL_SIZE // 2)
                    game_manager.place_tower(grid_pos)

        # Update game state
        game_manager.update(dt)

        # Check for game over
        game_over = game_manager.check_game_over()
        if game_over:
            print(f"Game Over! You {'won' if game_over == 'win' else 'lost'}!")
            running = False

        # Render
        screen.fill(WHITE)

        # Draw grid
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (SCREEN_WIDTH, y))

        # Draw path
        for i in range(len(game_manager.path) - 1):
            pygame.draw.line(screen, YELLOW, game_manager.path[i], game_manager.path[i+1], 5)

        # Draw game objects
        for tower in game_manager.towers:
            tower.components["render"].draw(tower, screen)
        for monster in game_manager.monsters:
            monster.components["render"].draw(monster, screen)

        # Draw UI
        font = pygame.font.Font(None, 36)
        currency_text = font.render(f"Currency: {game_manager.currency}", True, BLACK)
        wave_text = font.render(f"Wave: {game_manager.wave_number}", True, BLACK)
        time_text = font.render(f"Time: {int(game_manager.time_elapsed)}", True, BLACK)
        escaped_text = font.render(f"Escaped: {game_manager.monsters_escaped}/{game_manager.max_monsters_escaped}", True, BLACK)

        screen.blit(currency_text, (10, 10))
        screen.blit(wave_text, (10, 50))
        screen.blit(time_text, (10, 90))
        screen.blit(escaped_text, (10, 130))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
