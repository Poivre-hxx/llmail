import pygame
from enum import Enum
import random

# 初始化Pygame库
pygame.init()

# 设置窗口大小和标题
SCREEN_WIDTH, SCREEN_HEIGHT = 720, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('贪吃蛇游戏')

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class SnakeState(Enum):
    MOVING_LEFT = (-1, 0)
    MOVING_RIGHT = (1, 0)
    MOVING_UP = (0, -1)
    MOVING_DOWN = (0, 1)

# 定义蛇类
class Snake:
    def __init__(self):
        self.body = [(360, 240), (350, 240), (340, 240)]  # 初始化蛇的三个部分位置（头部，中段，尾部）
        self.direction = SnakeState.MOVING_LEFT
        self.snake_length = len(self.body)

    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        if len(self.body) > 1:
            # 移动蛇的其余部分与头部保持一致
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i] = self.body[i - 1]
                
        new_head_x, new_head_y = head_x + dx * 10, head_y + dy * 10
        
        # 更新头的位置（基于当前方向移动）
        # 处理 x 方向的环绕
        if new_head_x >= SCREEN_WIDTH:
            new_head_x = 0
        elif new_head_x < 0:
            new_head_x = SCREEN_WIDTH - 10
            
        # 处理 y 方向的环绕
        if new_head_y >= SCREEN_HEIGHT:
            new_head_y = 0
        elif new_head_y < 0:
            new_head_y = SCREEN_HEIGHT - 10
            
        self.body[0] = (new_head_x, new_head_y)  # 同时更新 x 和 y 坐标
        
        return new_head_x != head_x or new_head_y != head_y  # 检查蛇是否移动了

def game_loop():
    clock = pygame.time.Clock()
    snake = Snake()
    food_pos = None
    score = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        dx, dy = (snake.direction.value[0], snake.direction.value[1])
        
        # 根据按键更新蛇的方向
        if keys[pygame.K_LEFT]:
            snake.direction = SnakeState.MOVING_LEFT
        elif keys[pygame.K_RIGHT]:
            snake.direction = SnakeState.MOVING_RIGHT
        elif keys[pygame.K_UP]:
            snake.direction = SnakeState.MOVING_UP
        elif keys[pygame.K_DOWN]:
            snake.direction = SnakeState.MOVING_DOWN

        # 生成食物和检查碰撞
        if not food_pos or pygame.Rect(snake.body[0][0], snake.body[0][1], 10, 10).colliderect(
                pygame.Rect(food_pos[0], food_pos[1], 10, 10)):
            # 更新分数并重新生成食物位置
            score += 1
            food_pos = (random.randint(5, SCREEN_WIDTH - 10) // 10 * 10,
                       random.randint(5, SCREEN_HEIGHT - 10) // 10 * 10)
        
        elif not snake.move():
            # 蛇移动失败（撞到自己或边界）
            pygame.quit()
            return

        screen.fill((0, 0, 0))
        # 绘制蛇和食物
        for segment in snake.body:
            pygame.draw.rect(screen, WHITE, (segment[0], segment[1], 10, 10))
        if food_pos:
            pygame.draw.circle(screen, RED, food_pos, 5)
        
        pygame.display.flip()
        clock.tick(10)  # 控制游戏速度

if __name__ == '__main__':
    game_loop()