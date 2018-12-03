from gym.envs.registration import register

register(
    id='Glu-v0',
    entry_point='gym_GluttonousSnake.envs:GluttonousSnakeEnv',
)
