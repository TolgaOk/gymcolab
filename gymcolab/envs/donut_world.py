""" Donut world from DeepMDP: Gelada et al. (https://arxiv.org/abs/1906.02736)
"""
import gym
from gym import spaces
import numpy as np
import random
import pycolab
from pycolab.prefab_parts import sprites
from pycolab.ascii_art import Partial
from pycolab.cropping import ObservationCropper, ScrollingCropper

from gymcolab.colab_env import ColabEnv


def make_donut_map(size, outer_disk_multilier=1.0, inner_disk_multiplier=0.7):
    """ Construct a donut wolrd map.
        Arguments:
            - size: Length of the map's edge in terms of cell
            - outer_disk_multilier: Outer radius of the travelable region
                (default: 1.0)
            - outer_disk_multilier: Inner radius of the travelable region
                (default: 0.7)
        Return:
            - Map of the world as list of strings
    """
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
    """ Sprite of the agent that terminates the environment for a counter
    clockwise turn.
    """
    def __init__(self, corner, position, character):
        super().__init__(corner, position, character, impassable="#")
        self.init_angle = self.get_angle(corner, position)
        self.prev_angle = self.init_angle
        self.angular_pos = 0

    def get_angle(self, corner, position):
        row, col = position
        rows, cols = corner

        coord_y, coord_x = (rows//2 - row, col - cols//2)
        return np.arctan2(coord_y, coord_x)/np.pi + 1

    def _angle_diff(self, angle):
        if 0.0 <= angle < 0.5 and 1.5 < self.prev_angle <= 2.0:
            return angle + 2 - self.prev_angle
        if 0.0 <= self.prev_angle < 0.5 and 1.5 < angle <= 2.0:
            return angle - 2 - self.prev_angle
        else:
            return angle - self.prev_angle

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del backdrop, layers  # Unused

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

        corner = board.shape
        angle = self.get_angle(corner, things["P"].position)
        delta_angle = self._angle_diff(angle)
        self.angular_pos += delta_angle
        self.prev_angle = angle
        if self.angular_pos >= 2:
            self.angular_pos = 0
            the_plot.terminate_episode()
            the_plot.add_reward(1)


class WallDrape(pycolab.things.Drape):

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del self, actions, board, layers, backdrop, things, the_plot


class DonutWorld(ColabEnv):
    """ Circular 2D environment where the termination condition is to run
    counter clockwise for a single turn.
    Arguments:
        - size: Length of the edge of the world in turms of cell
        - cell_size: Size of each cell for renderer.
        - colors: Color dictionary that maps envionment characters to colors
        - render_croppers: Croppers for the renderer. Renderer initialize cells
            for each cropper. These croppers do not make any difference in the
            environment mechanics.
    """
    COLORS = {
        "P": "#00B8FA",
        " ": "#DADADA",
        "#": "#989898"
    }

    def __init__(self, size=13, cell_size=20, colors=None,
                 render_croppers=None):
        self.world_map = make_donut_map(size)
        super().__init__(cell_size=cell_size,
                         colors=colors or DonutWorld.COLORS,
                         render_croppers=render_croppers)

    def _init_game(self):
        game = pycolab.ascii_art.ascii_art_to_game(
            art=self.world_map,
            what_lies_beneath=" ",
            sprites={"P": Partial(PlayerSprite)},
            drapes={"#": Partial(WallDrape)},
            update_schedule=[["P"], ["#"]],
            z_order="#P"
        )
        return game
