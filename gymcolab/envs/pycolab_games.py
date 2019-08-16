from gymcolab.colab_env import ColabEnv
import numpy as np
import time

from pycolab.examples.scrolly_maze import COLOUR_FG, make_game


def rgb_to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(int(rgb[0]/1000*255),
                                           int(rgb[1]/1000*255),
                                           int(rgb[2]/1000*255))


class scrolly_maze(ColabEnv):

    def __init__(self):
        colors = {key: rgb_to_hex(rgb) for key, rgb in COLOUR_FG.items()}

        super().__init__(cell_size=20,
                         colors=colors)

    def _init_game(self):
        return make_game(0)


if __name__ == "__main__":
    env = scrolly_maze()
    env.reset()
    for i in range(2000):
        _, _, done, _ = env.step(np.random.randint(5))
        env.render()
        time.sleep(1)
        if done:
            env.reset()
