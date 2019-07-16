""" Render the game board, values and actions in a plot. Characters in the
game board will have the colors given to the renderer.
"""
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import time


class PlotRenderer():
    """ Matplotlib ploter.
    Parameters:
        - characters_colors: dictionary of colors for each character on the
        board
    """
    DEFAULT_COLOR = "#CCCCCC"
    plt.ion()
    
    def __init__(self, characters_colors):
        colors = [self.DEFAULT_COLOR]*256
        for key, value in characters_colors.items():
            if not (isinstance(value, str) or len(value) == 7 or
                    value.starts_with("#")):
                raise ValueError("Character colors must be hex in string type")
            colors[ord(key)] = value
        cm_name = "GridGame"
        n_bins = list(range(257))
        self.cm = LinearSegmentedColormap.from_list(cm_name, colors, N=256)

        self.fig = plt.figure()
        ax = self.fig.add_subplot(1, 1, 1)
        self.image_plot = ax.imshow(np.zeros((1, 1)), cmap=self.cm, vmin=0, vmax=255)

        self.is_animate = False

    def render(self, board):
        self.image_plot.set_array(board)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

if __name__ == "__main__":
    board = [[32, 32, 32, 32, 35],
             [32, 32, 32, 32, 35],
             [32, 32, 32, 32, 35],
             [32, 32, 80, 32, 35],
             [32, 32, 32, 32, 35],
             [32, 32, 32, 32, 35]]
    chr_to_color = {
        "P": "#DD3388",
        " ": "#BBBBBB",
        "#": "#221133"
    }
    env = PlotRenderer(chr_to_color)
    for i in range(100):
        env.render(board)
