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
        if is_enemy:
            self.color = random.choice(define.ALL_COLOR)
            self.position = random.randrange(10, 20), random.randrange(10, 200)
        else:
            self.position = random.randrange(5, 25), random.randrange(5, 25)
        self.body.append(self.position)
        self.is_enemy = is_enemy

        if not is_enemy:
            self.speed = 480
        self.path = [self.position] * 100

    def pos(self):
        print(self.position)

    def get_lenth(self):
        return len(self.body)

    def draw(self):
        index = 0
        for (x, y) in self.body:
            if index == 0:
                # head
                pygame.draw.circle(screen, self.color, [int((x + 0.5) * cell_width), int((y + 0.5) * cell_height)], int(cell_width / 2))

            else:
                #rect = Rect((x * cell_width, y * cell_height), ((x + 1) * cell_width, (y + 1) * cell_height))
                pygame.draw.rect(screen, self.color, (x * cell_width, y * cell_height, cell_width, cell_height))
            index += 1

    def isLegal(self, nx, ny):
        if nx < 0 or ny < 0 or nx >= field_width or ny >= field_height:
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
        self.direction = 'L'
        self.last_move = -1

    def right(self):
        self.direction = 'R'
        self.last_move = -1

    def down(self):
        self.direction = 'D'
        self.last_move = -1

    def up(self):
        self.direction = 'U'
        self.last_move = -1

    def update(self):
        self.draw()
        global game_over
        if self.last_move != -1 :#and time - self.last_move < self.speed:
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
            game_over = True
            return

        self.body.insert(0, (nx, ny))
        if field_map[ny][nx] == 1:
            # eat food
            self.color_degree += 5
            if self.color_degree > 255:
                self.color_degree = 255
            #self.color = pygame.Color(0, self.color_degree, 0)

            field_map[ny][nx] = 0
            index = 0
            for (fx, fy, _) in foods:
                if (fx, fy) == (nx, ny):
                    foods.pop(index)
                    break
                index += 1
        else:
            self.body.pop()

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
snake.pos()
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
    snake.draw()

    pygame.display.flip()
    image_data = pygame.surfarray.array3d(pygame.display.get_surface())
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                snake.up()
            elif event.key == K_a or event.key == K_LEFT:
                snake.left()
            elif event.key == K_d or event.key == K_RIGHT:
                snake.right()
            elif event.key == K_s or event.key == K_DOWN:
                snake.down()
            snake.update()
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
