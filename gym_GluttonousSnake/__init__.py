from gym.envs.registration import register

register(
    id='Glu-v0',
    entry_point='gym_GluttonousSnake.envs:GluttonousSnakeEnv',
)
register(
    id='Glu-v1',
    entry_point='gym_GluttonousSnake.envs:MultiGluttonousSnakeEnv',
)
register(
    id='Glu-v2',
    entry_point='gym_GluttonousSnake.envs:MultiGluttonousSnake2Env',
)
