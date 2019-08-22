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
from itertools import chain
from pycolab.prefab_parts import sprites
from pycolab.ascii_art import Partial
from gymcolab.colab_env import ColabEnv

WORLDMAP = ["##########",
            "#     B  #",
            "#        #",
            "#        #",
            "#    P   #",
            "#      b #",
            "#        #",
            "#        #",
            "#        #",
            "##########"]
PAIRING = {
    "B": ["b"],
}
ENV_LENGTH = 100
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

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del self, actions, board, layers, backdrop, things, the_plot


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
        self.env_length = ENV_LENGTH
        self.ball_of_interest = list(
            chain(*self.pairing.values()))

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
        # --------- Termination -------------
        inventory_size = sum(value for ball, value in
                             things["P"].inventory.items()
                             if ball in self.ball_of_interest)
        n_balls = sum(thing.curtain.any() for thing in things.values()
                      if isinstance(thing, BallDrape) and
                      thing.character in self.ball_of_interest)
        if inventory_size == 0 and n_balls == 0:
            the_plot.terminate_episode()

        self.env_length -= 1
        if self.env_length <= 0:
            the_plot.terminate_episode()
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
        "b": "#11C9C9",
        "c": "#00B8B8",
        "d": "#22DADA",
        "B": "#DAA822",
        "#": "#989898"
    }

    def __init__(self, balls, bucket, pairing=None, worldmap=None,
                 cell_size=40, colors=None, render_croppers=None):
        self.world_map = worldmap or WORLDMAP
        self.pairing = pairing or PAIRING
        self.balls = balls
        self.bucket = bucket
        assert isinstance(bucket, str), "Bucket must be a character"
        assert isinstance(balls, str), "Balls must be a string of characters"
        super().__init__(cell_size=cell_size,
                         colors=colors or self.COLORS,
                         render_croppers=render_croppers)

    def _init_game(self):
        drapes = {}
        for ball in self.balls:
            drapes[ball] = Partial(BallDrape)
        drapes["#"] = Partial(WallDrape)
        drapes[self.bucket] = Partial(BucketDrape, self.pairing)

        u_schedule = ([["P"], ["#"], [self.bucket]] +
                      [[char] for char in self.balls])

        z_order = "P" + self.balls + self.bucket + "#"

        game = pycolab.ascii_art.ascii_art_to_game(
            art=self.world_map,
            what_lies_beneath=" ",
            sprites={"P": Partial(PlayerSprite)},
            drapes=drapes,
            update_schedule=u_schedule,
            z_order=z_order
        )
        return game


if __name__ == "__main__":

    worldmap = ["##########",
                "#     B  #",
                "#   c    #",
                "#        #",
                "#    P   #",
                "#  b     #",
                "#      c #",
                "#  d     #",
                "#    d   #",
                "##########"]

    pairing = {
        "B": ["c"],
    }

    env = Warehouse(balls="cdb", bucket="B",
                    pairing=pairing, worldmap=worldmap)
    for i in range(800):
        done = False
        state = env.reset()
        while not done:
            action = random.randint(0, 4)
            state, reward, done, _ = env.step(action)
            env.render()
            print(reward, done)
            print(state.shape)
            time.sleep(0.1)
            if done:
                print("Done")
                break
