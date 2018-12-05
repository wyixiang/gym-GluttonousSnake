import pygame
from pygame.locals import *
import math
import random
import define
import time as t

class Snake():
    def __init__(self, is_enemy=False):
        self.field_width, self.field_height = 30, 30
        self.cell_width, self.cell_height = 20, 20
        self.direction = 'D'
        self.color_degree = 0
        # self.color = random.choice(define.ALL_COLOR)
        self.color = pygame.Color(0, self.color_degree, 0)
        self.speed = 300
        self.last_move = -1
        self.body = []
        self.game_over = False
        self.is_enemy = is_enemy
        self.killed = 0
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

    def isKill(self, myenemy):
        nx = self.nx
        ny = self.ny
        index = 0
        for s in myenemy:
            if s.body[0] == self.body[0]:
                continue
            for (x, y) in s.body:
                if index == len(s.body) - 1:
                    continue
                if (nx, ny) == (x, y):
                    self.killed = 1
                    return True
                index += 1
        return False

    def update_direc(self, action):
        self.last_move = -1
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
        self.draw(screen)
        if self.last_move != -1:
            return

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

    def becomefood(self, foods, field_map):
        for (x, y) in self.body:
            field_map[y][x] = 1
            foods.append((x, y, colors_for_foods[random.randint(0, len(colors_for_foods) - 1)]))

def drawFoods():
    for (x, y, color) in foods:
        pygame.draw.circle(screen, color, [int((x + 0.5) * cell_width), int((y + 0.5) * cell_height)], int(cell_width / 4))

def produceFood():
    while True:
        nfx, nfy = random.randint(0, field_width - 1), random.randint(0, field_height - 1)
        if (nfx, nfy) in snake.body:
            continue
        if field_map[nfy][nfx] == 1:
            continue
        
        field_map[nfy][nfx] = 1
        foods.append((nfx, nfy, colors_for_foods[random.randint(0, len(colors_for_foods) - 1)]))
        break

pygame.init()
field_width, field_height = 30, 30
cell_width, cell_height = 20, 20 
screen = pygame.display.set_mode((field_width * cell_width, field_height * cell_height), 0, 32)
pygame.display.set_caption('GluttonousSnake')

colors_for_foods = (
        pygame.Color(255, 0, 0), pygame.Color(0, 0, 255),
        pygame.Color(100, 100, 100), pygame.Color(100, 0, 200))
game_over_img = pygame.image.load("resources/images/game_over.gif")

game_over = False

foods = []
last_food_produce = -1
food_produce_interval = 4000
field_map = [[0 for i in range(field_width)] for j in range(field_height)]

snake = Snake()
enemy = []
for i in range(5):
    enemy.append(Snake(True))

while not game_over:
    screen.fill((255, 255, 255))
    time = pygame.time.get_ticks()
    if last_food_produce == -1 or time - last_food_produce >= food_produce_interval:
        produceFood()
        last_food_produce = time

    drawFoods()
    snake.draw(screen)
    for s in enemy:
        s.draw(screen)

    pygame.display.flip()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                snake.update_direc(0)
            elif event.key == K_a or event.key == K_LEFT:
                snake.update_direc(1)
            elif event.key == K_d or event.key == K_RIGHT:
                snake.update_direc(2)
            elif event.key == K_s or event.key == K_DOWN:
                snake.update_direc(3)
            snake.new_point()
            if not snake.isLegal() or snake.isKill(enemy):
                game_over = True
            else:
                snake.update(screen, foods, field_map)
            index = 0
            for s in enemy:
                s.update_direc(random.randint(0, 3))
                s.new_point()
                if not s.isLegal() or s.isKill(enemy) or s.isKill([snake]):
                    s.becomefood(foods, field_map)
                    enemy.pop(index)
                    enemy.append(Snake(True))
                    continue

                s.update(screen, foods, field_map)
                index += 1
    if game_over:
        break


screen.blit(game_over_img, ((field_width - 2) / 2 * cell_width, (field_height / 2 - 4) * cell_height))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    pygame.display.update()
