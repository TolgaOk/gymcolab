from gymcolab.envs.donut_world import DonutWorld
import numpy as np
import time

if __name__ == "__main__":
    env = DonutWorld()
    state = env.reset()
    for i in range(5000):
        state, reward, done, _ = env.step(np.random.randint(5))
        env.render()
        if done:
            env.reset()
            print(reward, done)
        print(state.shape)