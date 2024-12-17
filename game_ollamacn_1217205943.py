import pygame
from pygame.locals import *

# 初始化pygame模块和设置屏幕尺寸为720x480像素
pygame.init()
screen = pygame.display.set_mode((720, 480))

# 设置游戏标题
pygame.display.set_caption('Pixel Ark Adventure')

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([16, 16])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([16, 16])
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        # 移动敌人的简单实现（在x轴上移动）
        if self.rect.x > -16 and self.rect.x < screen.get_width():
            self.rect.x += 3
        else:
            self.rect.y -= 20

def draw_game_screen(screen, player, enemies):
    screen.fill((0, 0, 0))
    
    # 绘制角色和敌人
    screen.blit(player.image, player.rect)  # 绘制玩家
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)  # 绘制敌人
        
    pygame.display.flip()

# 游戏主循环
def game_loop():
    running = True
    clock = pygame.time.Clock()
    player = Player()
    enemies = pygame.sprite.GroupSingle()
    
    # 创建一个敌人
    enemy = Enemy()
    enemy.rect.x = screen.get_width() - 16
    enemy.rect.y = screen.get_height() // 2
    enemies.add(enemy)
    
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            # 检测按键事件并移动角色（改正后的按键事件处理）
            if event.type == KEYDOWN:
                if event.key == K_a or event.key == K_LEFT:
                    player.move(-3, 0)
                elif event.key == K_d or event.key == K_RIGHT:
                    player.move(3, 0)

        # 游戏逻辑（碰撞检测等）
        if pygame.sprite.collide_rect(player, enemy):
            print("Player collision with enemy!")
            running = False
            
        draw_game_screen(screen, player, enemies)
        
    pygame.quit()

game_loop()
