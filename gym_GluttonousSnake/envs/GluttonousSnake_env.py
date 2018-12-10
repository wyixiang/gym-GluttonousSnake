import gym

import pygame
import random


class GluttonousSnakeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.field_width, self.field_height = 15, 15
        self.cell_width, self.cell_height = 20, 20
        self.max_step = 2000
        self.food_produce_interval = 15
        self.last_food_produce = -1
        self.now_step = 0
        self.colors_for_foods = (
            pygame.Color(255, 0, 0), pygame.Color(0, 0, 255),
            pygame.Color(100, 100, 100), pygame.Color(100, 0, 200))

    def step(self, action):
        if action == 0:
            self.snake.up()
        elif action == 1:
            self.snake.left()
        elif action == 2:
            self.snake.right()
        elif action == 3:
            self.snake.down()

        self.screen.fill((255, 255, 255))
        self.now_step += 1
        t = self.now_step
        '''if self.last_food_produce == -1 or t - self.last_food_produce >= self.food_produce_interval:
            self.produceFood()
            self.last_food_produce = t'''

        self.drawFoods()
        self.snake.update(self.screen, self.foods, self.field_map)
        done = self.snake.game_over

        pygame.display.flip()
        pygame.display.update()
        image_data = pygame.display.get_surface()

        if not done:
            if self.snake.eat - self.last_eat > 0:
                reward = 10
                self.last_eat = self.snake.eat
                self.produceFood()
            else:
                reward = -0.2
        else:
            reward = -20

        if self.now_step == self.max_step - 1:
            done = True

        #state = image_data
        #image_data = pygame.transform.flip(pygame.display.get_surface(), True, True)
        image_data = pygame.transform.rotate(image_data, 90.0)
        image_data = pygame.transform.flip(image_data, False, True)
        state = pygame.surfarray.array3d(image_data)

        return state, reward, done, {}

    def reset(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.field_width * self.cell_width, self.field_height * self.cell_height), 0, 32)
        pygame.display.set_caption('GluttonousSnake')

        self.foods = []
        self.last_food_produce = -1
        self.field_map = [[0 for i in range(self.field_width)] for j in range(self.field_height)]
        self.snake = Snake()
        self.last_eat = 0

        self.now_step = 0

        self.screen.fill((255, 255, 255))
        self.snake.draw(self.screen)
        for i in range(1):
            self.produceFood()

        self.drawFoods()

        pygame.display.flip()
        pygame.display.update()
        image_data = pygame.display.get_surface()
        image_data = pygame.transform.rotate(image_data, 90.0)
        image_data = pygame.transform.flip(image_data, False, True)
        state = pygame.surfarray.array3d(image_data)


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
        self.field_width, self.field_height = 15, 15
        self.cell_width, self.cell_height = 20, 20
        self.direction = 'D'
        self.color_degree = 0
        # self.color = random.choice(define.ALL_COLOR)
        self.color = pygame.Color(0, self.color_degree, 0)
        self.speed = 300
        self.last_move = 0
        self.body = [(3, 3)]
        self.game_over = False
        self.init_lenth = 5
        self.eat = 0
        if is_enemy:
            self.position = random.randrange(300, 1300), random.randrange(200, 600)
        else:
            self.position = random.randrange(700, 900), random.randrange(350, 450)
        self.is_enemy = is_enemy

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

    def isLegal(self, nx, ny):
        if nx < 0 or ny < 0 or nx >= self.field_width or ny >= self.field_height:
            return False
        index = 0
        for (x, y) in self.body:
            if index == len(self.body) - 1:
                continue
            if (nx, ny) == (x, y):
                return False
            index += 1
        return True

    def left(self):
        if self.direction != 'R':
            self.direction = 'L'
        self.last_move = -1

    def right(self):
        if self.direction != 'L':
            self.direction = 'R'
        self.last_move = -1

    def down(self):
        if self.direction != 'U':
            self.direction = 'D'
        self.last_move = -1

    def up(self):
        if self.direction != 'D':
            self.direction = 'U'
        self.last_move = -1

    def update(self, screen, foods, field_map):
        if self.last_move != -1:
            return

        (hx, hy) = self.body[0]
        if self.direction == 'L':
            (nx, ny) = (hx - 1, hy)
        elif self.direction == 'R':
            (nx, ny) = (hx + 1, hy)
        elif self.direction == 'U':
            (nx, ny) = (hx, hy - 1)
        elif self.direction == 'D':
            (nx, ny) = (hx, hy + 1)
        if not self.isLegal(nx, ny):
            self.game_over = True
            return

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
                    self.eat += 1
                    break
                index += 1
        elif len(self.body) > self.init_lenth:
            self.body.pop()
        self.last_move = 0
        self.draw(screen)


