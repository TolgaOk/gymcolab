""" Warehouse environment from Graph-DQN
    http://spirl.info/2019/camera-ready/spirl_camera-ready_07.pdf
"""
import gym
from gym import spaces
import numpy as np
import random
import pycolab
import time
from collections import defaultdict
from pycolab.prefab_parts import sprites
from pycolab.ascii_art import Partial
from gymcolab.colab_env import ColabEnv

WORLDMAP = ["##########",
            "#     b  #",
            "#   b    #",
            "#        #",
            "#      B #",
            "#        #",
            "#     c  #",
            "#        #",
            "#   P    #",
            "##########"]
PAIRING = {
    "B": {"b", "c"},
}
ENV_LENGTH = 2000
PENALTY = -0.1
REWARD = 3.0


class PlayerSprite(sprites.MazeWalker):
    """ Sprite of the agent that terminates the environment for a counter
    clockwise turn.
    """

    def __init__(self, corner, position, character):
        super().__init__(corner, position, character, impassable="#")
        self.inventory = defaultdict(lambda: 0)

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del backdrop, layers  # Unused
        the_plot.add_reward(PENALTY)

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
    def __init__(self, curtain, character):
        super().__init__(curtain, character)
        self.env_length = ENV_LENGTH

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del actions, board, layers, backdrop
        # --------- Termination -------------
        inventory_size = sum(things["P"].inventory.values())
        n_balls = sum(thing.curtain.any() for thing in things.values()
                      if isinstance(thing, BallDrape))
        if inventory_size == 0 and n_balls == 0:
            the_plot.terminate_episode()
        
        self.env_length -= 1
        if self.env_length <= 0:
            the_plot.terminate_episode()
        # -----------------------------------


class BallDrape(pycolab.things.Drape):

    def __init__(self, curtain, character):
        super().__init__(curtain, character)
        assert self.character.islower(), ("Character for a Ball must be"
                                          "lowercase!")

    def update(self, actions, board, layers, backdrop, things, the_plot):

        # ------------- Take Ball ------------
        player_pattern_position = things['P'].position
        if self.curtain[player_pattern_position]:
            things["P"].inventory[self.character] += 1
            self.curtain[player_pattern_position] = False
        # -----------------------------------


class BucketDrape(pycolab.things.Drape):

    def __init__(self, curtain, character, pairing):
        super().__init__(curtain, character)
        assert self.character.isupper(), ("Character for a Bucket must be"
                                          "uppercase!")
        self.pairing = pairing

    def update(self, actions, board, layers, backdrop, things, the_plot):

        # ------------- To Bucket -----------
        player_pattern_position = things['P'].position
        if self.curtain[player_pattern_position]:
            n_balls = 0
            for ball_char in self.pairing[self.character]:
                n_balls += things["P"].inventory[ball_char]
                things["P"].inventory[ball_char] = 0
            the_plot.add_reward(n_balls * REWARD)
        # -----------------------------------


class Warehouse(ColabEnv):
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
        "b": "#DADA22",
        "c": "#DA22DA",
        "B": "#DAA822",
        "#": "#989898"
    }

    def __init__(self, pairing, worldmap, cell_size=20, colors=None,
                 render_croppers=None):
        self.world_map = worldmap
        self.pairing = pairing
        super().__init__(cell_size=cell_size,
                         colors=colors or self.COLORS,
                         render_croppers=render_croppers)

    def _init_game(self):
        game = pycolab.ascii_art.ascii_art_to_game(
            art=self.world_map,
            what_lies_beneath=" ",
            sprites={"P": Partial(PlayerSprite)},
            drapes={"#": Partial(WallDrape),
                    "b": Partial(BallDrape),
                    "c": Partial(BallDrape),
                    "B": Partial(BucketDrape, self.pairing)},
            update_schedule=[["P"], ["b"], ["c"], ["B"], ["#"]],
            z_order="PbcB#"
        )
        return game


if __name__ == "__main__":
    env = Warehouse(pairing=PAIRING, worldmap=WORLDMAP)
    for i in range(100):
        done = False
        state = env.reset()
        while not done:
            action = random.randint(0, 4)
            state, reward, done, _ = env.step(action)
            env.render()
            print(reward, done)
            time.sleep(0.01)
            if done:
                print("Done")
                break
