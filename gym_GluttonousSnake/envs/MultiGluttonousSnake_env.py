import gym

import pygame
import random


class MultiGluttonousSnakeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.field_width, self.field_height = 30, 30
        self.cell_width, self.cell_height = 20, 20
        self.max_step = 2000
        self.food_produce_interval = 20
        self.last_food_produce = -1
        self.now_step = 0
        self.colors_for_foods = (
            pygame.Color(255, 0, 0), pygame.Color(0, 0, 255),
            pygame.Color(100, 100, 100), pygame.Color(100, 0, 200))

    def step(self, action):
        reward = 0

        self.screen.fill((255, 255, 255))
        self.now_step += 1
        t = self.now_step
        if self.last_food_produce == -1 or t - self.last_food_produce >= self.food_produce_interval:
            self.produceFood()
            self.last_food_produce = t

        if not self.snake.update_direc(action):
            reward -= 1
        self.snake.new_point()
        if not self.snake.isLegal() or self.snake.isKill(self.enemy):
            self.snake.game_over = True
        else:
            self.snake.update(self.screen, self.foods, self.field_map)
        done = self.snake.game_over

        dead_snake_count = 0
        for s in self.enemy:
            s.update_direc(random.randint(0,3))
            s.new_point()
            if not s.isLegal() or s.isKill(self.enemy) or s.isKill([self.snake]):
                s.becomefood(self.foods, self.field_map)
                self.enemy.pop(self.enemy.index(s))
                dead_snake_count += 1
                continue

            s.update(self.screen, self.foods, self.field_map)

        for i in range(dead_snake_count):
            self.enemy.append(Snake(True))

        self.drawFoods()

        pygame.display.flip()
        pygame.display.update()
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())

        if not done:
            l = self.snake.get_lenth() - self.last_lenth
            if l > 0:
                self.last_lenth = self.snake.get_lenth()
                reward += 1
        else:
            reward -= 100

        if self.now_step == self.max_step:
            done = True

        state = image_data

        return state, reward, done, {}

    def reset(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.field_width * self.cell_width, self.field_height * self.cell_height), 0, 32)
        pygame.display.set_caption('GluttonousSnake')

        self.foods = []
        self.last_food_produce = -1
        self.field_map = [[0 for i in range(self.field_width)] for j in range(self.field_height)]
        self.snake = Snake()
        self.last_lenth = 1
        self.now_step = 0

        self.enemy = []
        for i in range(5):
            self.enemy.append(Snake(True))
            #print(self.enemy[i].color)

        self.screen.fill((255, 255, 255))

        self.snake.draw(self.screen)
        for s in self.enemy:
            s.draw(self.screen)
            self.produceFood()
        self.drawFoods()

        pygame.display.flip()
        pygame.display.update()
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        state = image_data

        return state

    def drawFoods(self):
        for (x, y, color) in self.foods:
            pygame.draw.circle(self.screen, color, [int((x + 0.5) * self.cell_width), int((y + 0.5) * self.cell_height)],
                               int(self.cell_width / 4))

    def produceFood(self):
        while True:
            nfx, nfy = random.randint(0, self.field_width - 1), random.randint(0, self.field_height - 1)
            if (nfx, nfy) in self.snake.body:
                continue
            if self.field_map[nfy][nfx] == 1:
                continue

            self.field_map[nfy][nfx] = 1
            self.foods.append((nfx, nfy, self.colors_for_foods[random.randint(0, len(self.colors_for_foods) - 1)]))
            break

    def render(self, mode="human", close=False):
        if close:
            self.close()

    def close(self):
        pygame.quit()
        exit(0)


class Snake():
    def __init__(self, is_enemy=False):
        self.field_width, self.field_height = 30, 30
        self.cell_width, self.cell_height = 20, 20
        self.direction = 'D'
        self.color_degree = 0
        # self.color = random.choice(define.ALL_COLOR)
        self.color = pygame.Color(0, self.color_degree, 0)
        self.speed = 300
        self.body = []
        self.game_over = False
        self.is_enemy = is_enemy
        self.killed = 0
        if is_enemy:
            self.color = random.choice(ALL_COLOR)
            self.position = random.randrange(5, 25), random.randrange(5, 25)
        else:
            self.position = random.randrange(10, 20), random.randrange(10, 20)
        self.body.append(self.position)
        self.is_enemy = is_enemy
        #print(self.position)

        if not is_enemy:
            self.speed = 480
        self.path = [self.position] * 100

    def get_lenth(self):
        return len(self.body)

    def draw(self, screen):
        index = 0
        for (x, y) in self.body:
            if index == 0:
                # head
                pygame.draw.circle(screen, self.color, [int((x + 0.5) * self.cell_width), int((y + 0.5) * self.cell_height)],
                                   int(self.cell_width / 2))

            else:
                # rect = Rect((x * cell_width, y * cell_height), ((x + 1) * cell_width, (y + 1) * cell_height))
                pygame.draw.rect(screen, self.color, (x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height))
            index += 1

    def isLegal(self):
        nx = self.nx
        ny = self.ny
        if nx < 0 or ny < 0 or nx >= self.field_width or ny >= self.field_height:
            return False
        if len(self.body) > 1 and (nx, ny) == self.body[1]:
            return False
        return True

    def isKill(self, enemy):
        nx = self.nx
        ny = self.ny
        for s in enemy:
            if s.body[0] == self.body[0]:
                continue
            for (x, y) in s.body:
                if (nx, ny) == (x, y):
                    self.killed = 1
                    return True
        return False

    def update_direc(self, action):
        if action == 0 and (self.direction != 'D' or len(self.body) == 1):
            #self.snake.up()
            self.direction = 'U'
        elif action == 1 and (self.direction != 'R' or len(self.body) == 1):
            #self.snake.left()
            self.direction = 'L'
        elif action == 2 and (self.direction != 'L' or len(self.body) == 1):
            #self.snake.right()
            self.direction = 'R'
        elif action == 3 and (self.direction != 'U' or len(self.body) == 1):
            #self.snake.down()
            self.direction = 'D'
        else:
            return False
        return True

    def new_point(self):
        (hx, hy) = self.body[0]
        if self.direction == 'L':
            (nx, ny) = (hx - 1, hy)
        elif self.direction == 'R':
            (nx, ny) = (hx + 1, hy)
        elif self.direction == 'U':
            (nx, ny) = (hx, hy - 1)
        elif self.direction == 'D':
            (nx, ny) = (hx, hy + 1)
        self.nx = nx
        self.ny = ny

    def update(self, screen, foods, field_map):
        nx = self.nx
        ny = self.ny

        self.body.insert(0, (nx, ny))
        if field_map[ny][nx] == 1:
            # eat food
            self.color_degree += 5
            if self.color_degree > 255:
                self.color_degree = 255
            # self.color = pygame.Color(0, self.color_degree, 0)

            field_map[ny][nx] = 0
            index = 0
            for (fx, fy, _) in foods:
                if (fx, fy) == (nx, ny):
                    foods.pop(index)
                    break
                index += 1
        elif len(self.body) > 5:
            self.body.pop()

        self.draw(screen)

    def becomefood(self, foods, field_map):
        for (x, y) in self.body:
            field_map[y][x] = 1
            foods.append((x, y, colors_for_foods[random.randint(0, len(colors_for_foods) - 1)]))


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_PINK = (255, 182, 193)
STEEL_BLUE = (70, 130, 180)
CRIMSON = (220, 20, 60)
VIOLET = (238, 130, 238)
SLATEBLUE = (106, 90, 205)
CYAN = (0, 255, 255)
AUQAMARIN = (127, 255, 170)
LIME = (0, 255, 0)
YELLOW = (255, 255, 0)
OLIVE = (128, 128, 0)
CORNISLK = (255, 248, 220)
ORANGE = (255, 165, 0)
CORAL = (255, 127, 80)

SKY_BLUE = (135, 206, 235, 255)
GOLD = (255, 215, 0, 255)
MAROON = (128, 0, 0, 255)
ALL_COLOR = (LIGHT_PINK, STEEL_BLUE, CRIMSON, VIOLET, SLATEBLUE, CYAN,
             AUQAMARIN, YELLOW, OLIVE, CORNISLK, ORANGE, CORAL)

colors_for_foods = (
            pygame.Color(255, 0, 0), pygame.Color(0, 0, 255),
            pygame.Color(100, 100, 100), pygame.Color(100, 0, 200))