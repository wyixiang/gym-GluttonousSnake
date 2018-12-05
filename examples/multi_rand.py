import gym
import gym_GluttonousSnake
import pygame
from pygame.locals import *


if __name__ == '__main__':
    env = gym.make('Glu-v1')

    while True:
        observation = env.reset()
        done = False
        action = 0

        while not done:
            flag = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == K_w or event.key == K_UP:
                        action = 0
                    elif event.key == K_a or event.key == K_LEFT:
                        action = 1
                    elif event.key == K_d or event.key == K_RIGHT:
                        action = 2
                    elif event.key == K_s or event.key == K_DOWN:
                        action = 3
                    flag = 1
            if flag == 0:
                continue

            newObservation, reward, done, info = env.step(action)