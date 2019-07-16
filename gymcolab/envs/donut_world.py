""" Donut world from: Gelada et al. (https://arxiv.org/abs/1906.02736)
"""

import gym
from gym import spaces
import numpy as np
import random
import pycolab
from pycolab.prefab_parts import sprites
from pycolab.ascii_art import Partial

from gymcolab.renderer.window_render import WindowRenderer
from gymcolab.base_grid import BaseEnv


def make_donut_map(size, outer_disk_multilier=1.0, inner_disk_multiplier=0.7):
    assert size > 10, "Size must be at least 11"
    assert size % 2 == 1, "Size must be odd"
    outer_radius = size//2
    inner_radius = (size*0.7)//2

    world_map = [["#" for i in range(size)] for j in range(size)]
    for row in range(size):
        for col in range(size):
            radius = np.sqrt((row - size//2)**2 + (col - size//2)**2)
            if inner_radius < radius and radius < outer_radius:
                world_map[row][col] = " "
    world_map[-2][size//2] = "P"
    for row in range(size):
        world_map[row] = "".join(world_map[row])
    return world_map


class PlayerSprite(sprites.MazeWalker):

    def __init__(self, corner, position, character):
        super().__init__(corner, position, character, impassable="#")

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del backdrop, things, layers  # Unused

        if actions == 0:    # go upward?
            self._north(board, the_plot)
        elif actions == 1:  # go downward?
            self._south(board, the_plot)
        elif actions == 2:  # go leftward?
            self._west(board, the_plot)
        elif actions == 3:  # go rightward?
            self._east(board, the_plot)
        elif actions == 4:  # do nothing?
            self._stay(board, the_plot)


class WallDrape(pycolab.things.Drape):

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del self, actions, board, layers, backdrop, things, the_plot


class DonutWorld(gym.Env, BaseEnv):

    COLORS = {
        "P": "#DD3388",
        " ": "#BBBBBB",
        "#": "#88CC77"
    }

    def __init__(self, size):
        world_map = make_donut_map(size)
        empty_space = np.argwhere(world_map == " ")
        game = pycolab.ascii_art.ascii_art_to_game(
            art=world_map,
            what_lies_beneath=" ",
            sprites={"P": Partial(PlayerSprite)},
            drapes={"#": Partial(WallDrape)},
            update_schedule=[["P"], ["#"]],
            z_order="#P"
        )
        BaseEnv.__init__(self, game)
        self.observation_space = self._map_observation_space()
        self.action_space = spaces.Discrete(5)

        self.renderer = WindowRenderer(self.col, self.row, self.COLORS)
        self._initial_reset = False

    def _observation(self, board):
        return self._to_map(board)

    def step(self, action):
        pass

    def render(self):
        pass

    def reset(self):
        if self._initial_reset is False:
            observation, reward, _ = self._game.its_showtime()
            self._initial_reset = True
        else:
            game.the_plot.terminate_episode()
        
    def seed(self):
        pass


if __name__ == "__main__":
    world_map = make_donut_map(11)
    for row in world_map:
        print(row)

    env = DonutWorld(11)
    for i in range(100):
        env.step(np.random.randint(5))
