import gym
import gym_GluttonousSnake
import time
import os
import json
import random
import numpy as np
from keras.models import Sequential, load_model
from keras.optimizers import RMSprop, Adam
from keras import optimizers, initializers
from keras.layers import Conv2D, Flatten, ZeroPadding2D
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.pooling import MaxPooling2D
import liveplot

import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.callbacks import TensorBoard
import cv2
import warnings
import matplotlib.pyplot as plt
import collections


class DeepQ:
    def __init__(self, outputs, memorySize, discountFactor, learningRate):
        self.output_size = outputs
        self.memory = collections.deque(maxlen=memorySize)
        #self.memory = ExperienceReplay((num_last_frames,) + model.input_shape[-2:], model.output_shape[-1], memory_size)
        self.gamma = discountFactor  # discount rate
        self.learningRate = learningRate
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        set_session(tf.Session(config=config))
        #self.model = self._build_model()
        self.model = self.createNatureDQN()
        self.target_model = self.createNatureDQN()
        self.target_model.set_weights(self.model.get_weights())

    def _build_model(self):
        model = Sequential()

        # Convolutions.
        model.add(Conv2D(
            16,
            kernel_size=(3, 3),
            strides=(1, 1),
            data_format='channels_first',
            input_shape=(img_channels, img_rows, img_cols)
        ))
        model.add(Activation('relu'))
        model.add(Conv2D(
            32,
            kernel_size=(3, 3),
            strides=(1, 1),
            data_format='channels_first'
        ))
        model.add(Activation('relu'))

        # Dense layers.
        model.add(Flatten())
        model.add(Dense(256))
        model.add(Activation('relu'))
        model.add(Dense(self.output_size))

        model.summary()
        model.compile(RMSprop(), 'MSE')

        return model

    def createNatureDQN(self):
        model = Sequential()
        model.add(Conv2D(32, (8, 8), strides=(4,4),
                         input_shape=(img_channels,img_rows,img_cols),
                         kernel_initializer=initializers.random_normal(stddev=0.01),
                         bias_initializer=initializers.Constant(value=0.01)))
        model.add(Activation('relu'))
        model.add(Conv2D(64, (4, 4), strides=(2,2),
                         kernel_initializer=initializers.random_normal(stddev=0.01),
                         bias_initializer=initializers.Constant(value=0.01)))
        model.add(Activation('relu'))
        model.add(Conv2D(64, (3, 3), strides=(1, 1),
                         kernel_initializer=initializers.random_normal(stddev=0.01),
                         bias_initializer=initializers.Constant(value=0.01)))
        model.add(Activation('relu'))
        model.add(Flatten())
        model.add(Dense(512,
                         kernel_initializer=initializers.random_normal(stddev=0.01),
                         bias_initializer=initializers.Constant(value=0.01)))
        model.add(Activation('relu'))
        model.add(Dense(self.output_size,
                         kernel_initializer=initializers.random_normal(stddev=0.01),
                         bias_initializer=initializers.Constant(value=0.01)))
        optimizer = optimizers.RMSprop(lr=self.learningRate)
        model.compile(loss="mse", optimizer=optimizer)
        model.summary()

        return model

    def addMemory(self, state, action, reward, newState, isFinal):
        self.memory.append((state, action, reward, newState, isFinal))

    def selectAction(self, state, explorationRate):
        act_values = self.model.predict(state)
        if np.random.rand() <= explorationRate:
            return random.randrange(self.output_size), np.max(act_values[0])
        return np.argmax(act_values[0]), np.max(act_values[0])

    def learnOnMiniBatch(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        X_batch = np.empty((0, img_channels, img_rows, img_cols), dtype=np.float64)
        Y_batch = np.empty((0, self.output_size), dtype=np.float64)
        for state, action, reward, next_state, done in minibatch:
            if done:
                target = reward
            else:
                target = (reward + self.gamma * np.max(self.target_model.predict(next_state)[0]))
            qValues = self.model.predict(state)
            Y_sample = qValues[0].copy()
            Y_sample[action] = target
            X_batch = np.append(X_batch, state.copy(), axis=0)
            Y_batch = np.append(Y_batch, np.array([Y_sample]), axis=0)
        self.model.train_on_batch(X_batch, Y_batch)

    def updateTargetNet(self):
        self.target_model.set_weights(self.model.get_weights())


    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


def get_format_state(observation):
    cv_image = cv2.cvtColor(observation, cv2.COLOR_BGR2GRAY)
    cv_image = cv2.resize(cv_image, (img_rows, img_cols))
    cv_image = 1.0 - np.asarray(cv_image, dtype='float64') / 250
    cv2.namedWindow("Image window", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image window", 300, 300)
    cv2.imshow("Image window", cv_image)
    cv2.waitKey(3)
    cv_image = np.asarray(cv_image, dtype='float64') * 5
    return cv_image

def get_last_frames(frames, observation):
    frame = observation
    if frames is None:
        frames = collections.deque([frame] * img_channels)
    else:
        frames.append(frame)
        frames.popleft()
    return np.expand_dims(frames, 0), frames


img_rows, img_cols, img_channels = 84, 84, 4

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    np.set_printoptions(suppress=True, precision=2, threshold=np.nan)

    env = gym.make('Glu-v3')
    outdir = '/tmp/GluttonousSnake_gym_experiments/'

    weights_path = './tmp/dqnnature/wights'
    plotter1 = liveplot.LivePlot(1)
    plotter2 = liveplot.LivePlot(2)
    plotter3 = liveplot.LivePlot(3, line_color='red')

    episode_count = 10000000
    max_steps = 2000
    minibatch_size = 32
    learningRate = 0.001
    discountFactor = 0.95
    memorySize = 50000
    learnStart = 500
    network_outputs = 4
    EXPLORE = 500000
    INITIAL_EPSILON = 1  # starting value of epsilon
    FINAL_EPSILON = 0.1  # final value of epsilon
    explorationRate = INITIAL_EPSILON
    stepCounter = 0
    loadsim_seconds = 0

    agent = DeepQ(network_outputs, memorySize, discountFactor, learningRate)

    last100Rewards = [0] * 100
    last100Scores = [0] * 100
    last100Index = 0
    last100Filled = False
    highest_reward = 0
    highest_score = 0
    start_time = time.time()

    total_step = 0
    data1 = []
    data2 = []
    data3 = []

    #start iterating from 'current epoch'.
    for epoch in range(episode_count):
        observation = env.reset()
        observation = get_format_state(observation)
        frames = None
        state, frames = get_last_frames(frames, observation)

        cumulated_reward = 0

        for t in range(max_steps):
            total_step += 1
            action, qValues = agent.selectAction(state, explorationRate)
            data3.append(qValues)
            #print(state)

            newObservation, reward, done, total_score = env.step(action)
            #print(reward)
            newObservation = get_format_state(newObservation)
            newstate, frames = get_last_frames(frames, newObservation)
            cumulated_reward += reward
            if highest_reward < cumulated_reward:
                highest_reward = cumulated_reward

            agent.addMemory(state, action, reward, newstate, done)
            state = newstate

            stepCounter += 1

            if stepCounter == learnStart:
                print("Starting learning")

            if stepCounter >= learnStart:
                agent.learnOnMiniBatch(minibatch_size)

            if stepCounter % 1000 == 0:
                agent.target_model.set_weights(agent.model.get_weights())

            if explorationRate > FINAL_EPSILON and stepCounter > learnStart:
                explorationRate -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

            if done:
                last100Rewards[last100Index] = cumulated_reward
                last100Scores[last100Index] = total_score
                data1.append(total_score)
                data2.append(cumulated_reward)
                last100Index += 1
                total_seconds = int(time.time() - start_time + loadsim_seconds)
                m, s = divmod(total_seconds, 60)
                h, m = divmod(m, 60)
                if last100Index >= 100:
                    last100Filled = True
                    last100Index = 0
                if not last100Filled:
                    print("EP "+"%3d"%epoch +" -{:>4} steps".format(t+1) + " - total step:" + "%4d"%total_step +" - CReward: "+"%3d"%cumulated_reward+" - Score: "+"%3d"%total_score +"  Eps="+"%3.2f"%explorationRate +"  Time: %d:%02d:%02d" % (h, m, s))
                else:
                    print("EP " + str(epoch) +" -{:>4} steps".format(t+1) + " - total step:" + "%5d"%total_step +" - last100 C_Rewards : " + "%4.1f" % ((sum(last100Rewards) / len(last100Rewards))) + " - CReward: " + "%5.1f" % cumulated_reward +" - last100 Scores : " + "%4.1f" % ((sum(last100Scores) / len(last100Scores))) + " - Score: " + "%3d" % total_score + "  Eps=" + "%3.2f" % explorationRate + "  Time: %d:%02d:%02d" % (h, m, s))

                    if epoch >= 2000 and (epoch)%50==0:
                        agent.save(weights_path+str(epoch))
                break

        if epoch % 10 == 0:
            plotter1.plot(data1, average=10)
            plotter2.plot(data2, average=10)
            plotter3.plot(data3)

    env.close()