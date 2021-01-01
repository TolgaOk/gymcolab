""" Very simple maze environment
"""
import gym
from gym import spaces
import numpy as np
import random
import pycolab
import time
from pycolab.prefab_parts import sprites
from pycolab.ascii_art import Partial
from pycolab.cropping import ObservationCropper, ScrollingCropper

from gymcolab.colab_env import ColabEnv

WORLDMAP = ["##########",
            "#        #",
            "#   @    #",
            "#        #",
            "#        #",
            "#        #",
            "##### ####",
            "#        #",
            "#P       #",
            "##########"]

ROOMWORLD = ["################",
             "#       #      #",
             "#       #      #",
             "#       #  P   #",
             "#              #",
             "#       #      #",
             "#       #      #",
             "### ######## ###",
             "#       #      #",
             "#       #      #",
             "#       #      #",
             "#  @           #",
             "#       #      #",
             "#       #      #",
             "################"]


class PlayerSprite(sprites.MazeWalker):
    """ Sprite of the agent that terminates the environment for a counter
    clockwise turn.
    """

    def __init__(self, corner, position, character):
        super().__init__(corner, position, character, impassable="#")

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


class WallDrape(pycolab.things.Drape):

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del self, actions, board, layers, backdrop, things, the_plot


class CashDrape(pycolab.things.Drape):
    """A `Drape` handling all of the coins.

    This Drape detects when a player traverses a coin, removing the coin and
    crediting the player for the collection. Terminates if all coins are gone.
    """
    def __init__(self, curtain, character):
        super().__init__(curtain, character)
        self.env_length = 200

    def update(self, actions, board, layers, backdrop, things, the_plot):
        player_pattern_position = things['P'].position

        if self.env_length <= 0:
            self.env_length = 200
            the_plot.add_reward(-1)
            the_plot.terminate_episode()
        else:
            if self.curtain[player_pattern_position]:
                the_plot.add_reward(1)
                self.curtain[player_pattern_position] = False
                if not self.curtain.any():
                    the_plot.terminate_episode()
            else:
                the_plot.add_reward(-1)
                self.env_length -= 1


class SimpleMaze(ColabEnv):
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
        "@": "#DADA22",
        "#": "#989898"
    }

    def __init__(self, cell_size=50, colors=None,
                 render_croppers=None, worldmap=None):
        self.world_map = worldmap or WORLDMAP
        super().__init__(cell_size=cell_size,
                         colors=colors or self.COLORS,
                         render_croppers=render_croppers)

    def _init_game(self):
        game = pycolab.ascii_art.ascii_art_to_game(
            art=self.world_map,
            what_lies_beneath=" ",
            sprites={"P": Partial(PlayerSprite)},
            drapes={"#": Partial(WallDrape),
                    "@": Partial(CashDrape)},
            update_schedule=[["P"], ["#"], ["@"]],
            z_order="#P@"
        )
        return game


if __name__ == "__main__":
    croppers = [
        ScrollingCropper(rows=5, cols=5, to_track=['P'],
                         initial_offset=(8, 1), pad_char="#", scroll_margins=(2, 2)),
        ObservationCropper()
    ]
    env = SimpleMaze(render_croppers=croppers)
    for i in range(100):
        done = False
        state = env.reset()
        print(state.shape)
        while not done:
            action = random.randint(0, 4)
            state, reward, done, _ = env.step(action)
            env.render()
            time.sleep(0.1)
            if done:
                print("Done")
                break
