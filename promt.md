## Snake

#### ollama

en prompt

prompt：Game Design Prompt: Classic Snake Game

Objective:
Design a classic snake game with the following guidelines:

**Core Gameplay and Mechanics:**
1. The game consists of a player-controlled snake that navigates through a rectangular grid-based environment to collect food items while avoiding collisions with its own body or boundaries.
2. The snake grows in length when it consumes food, which is randomly placed on the grid, creating additional challenges as space becomes more limited.

**Python-Ready Structure:**
1. **Game Objects**:
   - Snake: Defined by its head and body segments (initially three segments). Snake objects should have movement capabilities such as up, down, left, right, and growing in length when it eats food.
   - Food: Randomly placed on the grid. When consumed, the snake grows one segment longer.
2. **User Interaction**:
   - Control: Use arrow keys or WASD to navigate Snake across the grid.
3. **Events**:
   - Collision with the wall (when Snake hits the boundary of the game area) or with its own body is a loss condition.

**Win and Lose Conditions:**
- Win Condition: The game has no specific win condition since there's an inherent limit in avoiding collision; however, players strive to grow as long as possible without colliding.
- Lose Condition: Losing is when the snake collides with any part of its own body or the boundaries of the grid.

**Classic Gameplay Elements:**
1. **Scoring**:
   - Increase score based on food consumed (e.g., each piece of food adds 10 points).
2. **Levels and Challenges**:
   - No explicit levels but increasing difficulty as length grows, making collision avoidance more complex.

**Basic Rules and Interaction:**
- Movement Controls: Use arrow keys or WASD to change snake's direction upon pressing the key.
- Collisions: Snake cannot touch its own body or grid boundaries to avoid losing.

**Code Structure Suggestion**:
Implement a main game loop that handles user input, collision detection (snake with self and border), food generation, score updating, and logic for snake movement based on arrow key presses.

Your final implementation should allow for easy adjustments of speed settings, initial length of the snake, size of the playing area etc., offering customization options for different playstyles or skill levels.

This prompt lays out a clear vision for creating a Python-based version of the classic snake game while maintaining simplicity and focusing on core mechanics that translate directly into code.

cn prompt

项目名称：经典贪吃蛇游戏

1. **背景介绍**：
   - 游戏概念源自1976年的《Pong》（保龄球）之后，在1978年诞生的《Space Invaders》（太空入侵者）和《Snake》（贪吃蛇）游戏，是一款简单而具有极大挑战性的游戏。

2. **游戏规则**：
   - 玩家控制一条由像素块组成的“蛇”，在屏幕上移动。
   - 目标是通过不断吃到屏幕上的小点来增长自己的蛇的长度。
   - 游戏面板分为多个行和列，每个格子可以是空的或者有障碍物，玩家不能穿过这些障碍物。
   - 面板的四周有墙壁包围，即游戏开始时，玩家只能在面板内部移动。

3. **得分机制**：
   - 每次蛇吃到小点，会增加一条新的像素块在它的尾部，这会使蛇增长一节。
   - 蛇不能吃自己的身体。当身体的任何部分与头部碰撞，游戏即结束，并显示分数和游戏提示“Game Over”。

4. **速度调整**：
   - 游戏速度随得分自动增加。每次吃到小点后，游戏的速度会提高一点。
   - 增加速度之后，蛇必须更快地移动以维持其增长状态。

5. **特殊功能**（可选）：
   - 提供“加速”或“减速”道具作为随机事件，玩家通过吃到特定类型的小点获得，可以短暂改变游戏的速度。
   - 设置一个“重生点”，在被吃掉后的某个时间点允许玩家选择重新开始游戏。

6. **用户界面**：
   - 游戏屏幕清晰地显示得分、生命值（未考虑的情况下可简化为1个生命）和当前速度。
   - 背景音乐简单欢快，提供不同的音轨供选择或自定义。

7. **控制**：
   - 使用键盘的方向键（上、下、左、右）进行蛇的移动控制。
   - 空格键用于暂停游戏，Esc键退出游戏。

8. **视觉效果**：
   - 动画清晰流畅，展示食物和蛇的生长过程。
   - 蛇在碰撞时具有适当的物理反馈（例如，瞬间停止后反弹）。

9. **适应性**：
   - 游戏适合多平台使用：PC、移动设备或游戏机。
   - 语言选择上提供中英双语或者更多支持。

#### claude

Game: Classic Snake

Core Gameplay:
Create a simple Snake game where the player controls a snake that moves around a 2D grid. The snake grows longer as it eats food items that appear randomly on the grid.

Game Structure:
1. Grid: Create a 20x20 grid as the game board.
2. Snake: Represent the snake as a list of coordinates, starting with length 3.
3. Food: Generate food at random empty grid positions.

Controls:
- Use arrow keys (Up, Down, Left, Right) to change the snake's direction.
- The snake moves continuously in the current direction.

Game Mechanics:
1. Snake movement: Update the snake's position every frame based on its direction.
2. Collision detection: Check for collisions with walls, food, and the snake's own body.
3. Growing: Increase the snake's length by 1 when it eats food.
4. Food spawning: Generate new food when the current food is eaten.

Win/Lose Conditions:
- Lose: The game ends if the snake collides with the wall or its own body.
- Win: No specific win condition; aim for the highest score possible.

Scoring:
- Increase the score by 1 for each food item eaten.
- Display the current score on the screen.

Levels/Challenges:
- Increase the snake's speed slightly after every 5 food items eaten.
- (Optional) Add obstacles on the grid that the snake must avoid.

Basic Rules:
1. The snake cannot reverse direction instantly (e.g., cannot go right if currently moving left).
2. The game continues until the player loses.
3. Allow the player to restart the game after losing.
