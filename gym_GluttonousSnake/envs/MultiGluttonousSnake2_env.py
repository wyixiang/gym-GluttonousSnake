import gym
import gym_GluttonousSnake

import pygame
import random
import math
import os

from gym_GluttonousSnake.envs import define


class MultiGluttonousSnake2Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.field_width, self.field_height = 30, 30
        self.cell_width, self.cell_height = 20, 20
        self.max_step = 2000
        self.food_produce_interval = 20
        self.last_food_produce = -1
        self.now_step = 0
        self.food_dim = 3
        self.colors_for_foods = (
            pygame.Color(255, 0, 0), pygame.Color(0, 0, 255),
            pygame.Color(100, 100, 100), pygame.Color(100, 0, 200))
        print(os.path.dirname(gym_GluttonousSnake.__file__))

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
        dead_list = []
        for s in self.enemy:
            s.update_direc(random.randint(0,3))
            s.new_point()
            if not s.isLegal() or s.isKill(self.enemy) or s.isKill([self.snake]):
                s.becomefood(self.foods, self.field_map)
                dead_list.append(self.enemy.index(s))
                dead_snake_count += 1
                continue

            s.update(self.screen, self.foods, self.field_map)

        for i in dead_list:
            self.enemy.pop(i)
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
        self.field_map = [[0 for i in range(self.field_width*self.food_dim)] for j in range(self.field_height*self.food_dim)]
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
            pygame.draw.circle(self.screen, color, [int((x/self.food_dim + 0.5) * self.cell_width), int((y/self.food_dim + 0.5) * self.cell_height)],
                               int(self.cell_width / 4))

    def produceFood(self):
        while True:
            nfx, nfy = random.randint(0, self.field_width*self.food_dim - 1), random.randint(0, self.field_height*self.food_dim - 1)
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
        self.direction = 270.0
        self.color_degree = 0
        # self.color = random.choice(define.ALL_COLOR)
        self.color = pygame.Color(0, self.color_degree, 0)
        self.speed = 300
        self.body = []
        self.game_over = False
        self.is_enemy = is_enemy
        self.killed = 0
        self.eat_count = 5
        self.food_dim = 3
        if is_enemy:
            self.color = random.choice(define.ALL_COLOR)
            self.position = random.randrange(5, 25), random.randrange(5, 25)
        else:
            self.position = random.randrange(10, 20), random.randrange(10, 20)
        self.body.append(self.position)
        self.is_enemy = is_enemy
        #print(self.position)

        if not is_enemy:
            self.speed = 480
        self.path = [self.position] * 100

        cell_width, cell_height = self.cell_width, self.cell_height

        self.head = pygame.image.load(os.path.dirname(gym_GluttonousSnake.__file__) + "/envs/circle.png")
        self.head = pygame.transform.scale(self.head, (cell_width, cell_height))
        pygame.draw.circle(self.head, self.color, [int(0.50 * cell_width), int(0.5 * cell_height)], int(cell_width / 2))
        pygame.draw.circle(self.head, define.WHITE, [int(0.25 * cell_width), int(0.5 * cell_height)], int(cell_width / 4))
        pygame.draw.circle(self.head, define.WHITE, [int(0.75 * cell_width), int(0.5 * cell_height)], int(cell_width / 4))
        pygame.draw.circle(self.head, define.BLACK, [int(0.25 * cell_width), int(0.5 * cell_height)], int(cell_width / 6))
        pygame.draw.circle(self.head, define.BLACK, [int(0.75 * cell_width), int(0.5 * cell_height)], int(cell_width / 6))
        self.newhead = self.head


    def get_lenth(self):
        return len(self.body)

    def draw(self, screen):
        index = 0
        for (x, y) in self.body:
            if index == 0:
                # head
                screen.blit(self.newhead, [int((x ) * self.cell_width), int((y ) * self.cell_height)])

            else:
                # rect = Rect((x * cell_width, y * cell_height), ((x + 1) * cell_width, (y + 1) * cell_height))
                pygame.draw.circle(screen, self.color,
                                   [int((x + 0.5) * self.cell_width), int((y + 0.5) * self.cell_height)],
                                   int(self.cell_width / 2))
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
                if (nx - x)**2 +(ny - y)**2 < 1:
                    self.killed = 1
                    return True
        return False

    def update_direc(self, action):
        if action == 0:
            #self.snake.up()
            if self.direction < 270.0:
                self.direction = self.direction * 0.4 + 90 * 0.6
            else:
                self.direction = (self.direction - 360) * 0.4 + 90 * 0.6
        elif action == 1 and (self.direction != 'R' or len(self.body) == 1):
            #self.snake.left()
            self.direction = self.direction * 0.4 + 180 * 0.6
        elif action == 2 and (self.direction != 'L' or len(self.body) == 1):
            #self.snake.right()
            if self.direction < 180.0:
                self.direction = self.direction * 0.4 + 0 * 0.6
            else:
                self.direction = self.direction * 0.4 + 360 * 0.6
        elif action == 3 and (self.direction != 'U' or len(self.body) == 1):
            #self.snake.down()
            if self.direction > 90.0:
                self.direction = self.direction * 0.4 + 270 * 0.6
            else:
                self.direction = (self.direction + 360) * 0.4 + 270 * 0.6

        self.newhead = pygame.transform.rotate(self.head, self.direction - 90)
        return True

    def new_point(self):
        (hx, hy) = self.body[0]
        (nx, ny) = (hx + math.cos(math.radians(self.direction)), hy - math.sin(math.radians(self.direction)))
        self.nx = nx
        self.ny = ny

    def update(self, screen, foods, field_map):
        nx = self.nx
        ny = self.ny
        field_width, field_height = self.field_width, self.field_height
        food_dim = self.food_dim

        self.body.insert(0, (nx, ny))
        for i in range(-1, 2):
            for j in range(-1, 2):
                x = int(nx * food_dim) + i
                y = int(ny * food_dim) + j
                x = min(x, field_width * food_dim - 1)
                x = max(x, 0)
                y = min(y, field_height * food_dim - 1)
                y = max(y, 0)
                if field_map[y][x] == 1:
                    # eat food
                    self.color_degree += 5
                    if self.color_degree > 255:
                        self.color_degree = 255
                    # self.color = pygame.Color(0, self.color_degree, 0)

                    field_map[y][x] = 0
                    index = 0
                    for (fx, fy, _) in foods:
                        if (fx, fy) == (x, y):
                            foods.pop(index)
                            break
                        index += 1
                    self.eat_count += 1
        if self.eat_count > 0:
            self.eat_count -= 1
        else:
            self.body.pop()

        self.draw(screen)

    def becomefood(self, foods, field_map):
        food_dim = self.food_dim
        colors_for_foods = (
            pygame.Color(255, 0, 0), pygame.Color(0, 0, 255),
            pygame.Color(100, 100, 100), pygame.Color(100, 0, 200))
        for (x, y) in self.body:
            if field_map[int(y * food_dim)][int(x * food_dim)] == 0:
                field_map[int(y * food_dim)][int(x * food_dim)] = 1
                foods.append(
                    (int(x * food_dim), int(y * food_dim), colors_for_foods[random.randint(0, len(colors_for_foods) - 1)]))