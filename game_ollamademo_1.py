import pygame
import sys

# 初始化pygame模块
pygame.init()

# 设置窗口大小和标题
WINDOW_WIDTH, WINDOW_HEIGHT = 720, 480
pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('超级贪吃蛇')

# 设置分数、生命值等变量初始化
score = 0
lives = 1

# 定义颜色
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 初始化游戏屏幕和字体
screen = pygame.display.get_surface()
pygame.display.update()
font = pygame.font.Font(None, 36)

class Snake:
    def __init__(self):
        self.segments = [(360, 240), (350, 240), (340, 240)]  
        self.direction = 'RIGHT'

    def move(self):
        head_x, head_y = self.segments[0]
        if self.direction == 'LEFT':
            new_head_x, new_head_y = head_x - 10, head_y
        elif self.direction == 'RIGHT':
            new_head_x, new_head_y = head_x + 10, head_y
        elif self.direction == 'UP':
            new_head_x, new_head_y = head_x, head_y - 10
        else: 
            new_head_x, new_head_y = head_x, head_y + 10

        if (new_head_x < 0 or new_head_x >= WINDOW_WIDTH) or \
           (new_head_y < 0 or new_head_y >= WINDOW_HEIGHT):
           return False

        self.segments.insert(0, (new_head_x, new_head_y))
        try:
            self.segments.pop()
        except IndexError:
            pass
        return True
    
    def draw(self):
        for index, pos in enumerate(self.segments):
            x, y = pos[0], pos[1]
            color = GREEN if index == 0 else WHITE
            pygame.draw.rect(screen, color, (x * 10, y * 10, 10, 10))

    def check_collision(self):
        global score, lives
        head_x, head_y = self.segments[0]
        for segment in self.segments[1:]:
            if segment == (head_x, head_y) and len(self.segments) > 2:
                return False
        return True

def game():
    snake = Snake()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                new_direction = {'LEFT': 'RIGHT', 'RIGHT': 'LEFT', 
                                 'UP': 'DOWN', 'DOWN': 'UP'}.get(event.key)
                if new_direction and snake.direction != new_direction:
                    snake.direction = new_direction

        screen.fill(WHITE)

        # 检测碰撞和移动
        game_over = not snake.move()
        
        snake.draw()

        text = font.render(f"分数: {score}  生命值：{lives}", True, GREEN)
        screen.blit(text, (10, 10))
        
        if game_over:
            # 游戏结束处理
            score_text = font.render('游戏结束，你的分数为: '+str(score), True, RED)
            lives_text = font.render('剩余生命值：'+str(lives), True, GREEN)
            screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2))
            screen.blit(lives_text, (WINDOW_WIDTH // 2 - lives_text.get_width() // 2, WINDOW_HEIGHT // 2 + 30))
            pygame.display.update()
            pygame.time.wait(2000)
            return

        pygame.display.flip()

if __name__ == "__main__":
    game()
