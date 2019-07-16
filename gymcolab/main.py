""" Test script
"""

import numpy as np
import pycolab
from pycolab import ascii_art
from pycolab import human_ui
from pycolab.prefab_parts import sprites, drapes
from pycolab.things import Drape
import curses

WOLRD_ART = [
    '##############################',
    '#              #             #',
    '#              #             #',
    '#              #             #',
    '#              #             #',
    '###  ###  ######  ######  ####',
    '#      #               #     #',
    '#      #               #     #',
    '#      #               #   P #',
    '##############################'
]

FG_COLORS = {"P": (999, 500, 0),
             '#': (700, 700, 700),
             " ": (500, 770, 0)}
BG_COLORS = {"P": (999, 500, 0),
             '#': (700, 700, 700),
             " ": (500, 770, 0)}


class PlayerSprite(sprites.MazeWalker):

    def __init__(self, corner, position, character):
        super().__init__(corner, position, character, impassable="#",
                         egocentric_scroller=True)

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


class WallDrape(Drape):

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del self, actions, board, layers, backdrop, things, the_plot


def start_terminal(game):
    ui = human_ui.CursesUi(
        keys_to_actions={
            # Basic movement.
            curses.KEY_UP: 0,
            curses.KEY_DOWN: 1,
            curses.KEY_LEFT: 2,
            curses.KEY_RIGHT: 3,
        },
        delay=5,
        colour_fg=FG_COLORS,
        colour_bg=BG_COLORS)

    ui.play(game)


if __name__ == "__main__":
    import time
    import random
    from renderer import plot_renderer, window_render
    # renderer = plot_renderer.PlotRenderer({"P": "#DD3388",
    #                                        " ": "#BBBBBB",
    #                                        "#": "#221133"})
    renderer = window_render.WindowRenderer(900, 300, {"P": "#DD3388",
                                                       " ": "#BBBBBB",
                                                       "#": "#88CC77"},
                                            border_ratio=0.05)
    game = ascii_art.ascii_art_to_game(
        WOLRD_ART,
        what_lies_beneath=" ",
        sprites={"P": ascii_art.Partial(PlayerSprite)},
        drapes={"#": ascii_art.Partial(WallDrape)},
        update_schedule=[["P"], ["#"]],
        z_order="#P"
    )

    observation, reward, _ = game.its_showtime()
    while not game.game_over:
        # print(dir(game.things["P"]))
        # print(game.things["P"].position.col, game.things["P"].position.row)
        # print(game.things.keys(), game.backdrop)
        print(observation.layers.keys(), list(game.backdrop.palette))
        renderer.render(observation.board)
        action = random.randint(0, 3)
        observation, reward, _ = game.play(action)
