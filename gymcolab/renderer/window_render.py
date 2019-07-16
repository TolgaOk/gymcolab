""" Render the game board, values and actions in a window. Characters in the
game board will have the colors given to the renderer.
"""
from matplotlib.colors import LinearSegmentedColormap
import tkinter
import numpy as np
from itertools import product
from collections import defaultdict
import threading


class WindowRenderer():
    """ Tkinter based GUI renderer.
    """
    DEFAULT_COLOR = "#CCCCCC"

    def __init__(self, width, height, colors, border_ratio=0.05):
        self.root = tkinter.Tk()
        self.root.title("GridEnv")
        self.canvas = tkinter.Canvas(
            self.root, width=width, height=height, bg="gray")
        self.canvas.pack()
        self.canvas_height = height
        self.canvas_widht = width

        self.boarder_ratio = border_ratio
        self.colors = defaultdict(lambda: DEFAULT_COLOR)
        for key, value in colors.items():
            self.colors[ord(key)] = value

    def _init_render(self, board):
        height, width = board.shape
        cell_width = self.canvas_widht//width
        cell_height = self.canvas_height//height

        rows = self.canvas_height//cell_height
        cols = self.canvas_widht//cell_width

        b_w = int(cell_width*self.boarder_ratio)
        b_h = int(cell_height*self.boarder_ratio)

        cells = [self.canvas.create_rectangle(x*cell_width + b_w,
                                              y*cell_height + b_h,
                                              (x+1)*cell_width - b_w,
                                              (y+1)*cell_height - b_h)
                 for x, y in product(range(cols), range(rows))]
        return cells

    def render(self, board):
        try:
            self.cells
        except AttributeError:
            self.cells = self._init_render(board)

        for i, v in enumerate(board.flatten("F")):
            self.canvas.itemconfig(self.cells[i], fill=self.colors[v])
        self.root.update()


if __name__ == "__main__":
    COLORS = {
        0: "#BB33CC",
        1: "#22CC66",
        2: "#CC4499"
    }
    renderer = WindowRenderer(800, 800, COLORS)
    X, Y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20))
    for i in range(10000):
        Z = np.sin((X**2 + Y**2)*((i % 100)/50))
        Z = np.digitize(Z, [-0.4, 0.4])
        renderer.render(Z)
