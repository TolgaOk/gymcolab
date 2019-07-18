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
    """ Tkinter based GUI renderer. Each frame is rendered using cells. These
    cells are colored based on the croppers. Cropper objects provide
    observations from the game to render. These croppers can crop the whole
    game in which there is no cropping or scrolly croppers that follows a
    sprite. Frames from the croppers are colored based on the <colors>
    argument. Before the fist call of the renderer GUI window does not pop up.
    Therefore it can be initialized even if it won't be used without poping up
    the window.
    Arguments:
        - cell_size: Size of each cell in terms of pixel
        - colors: Color dictionary to map each character to its corresponding
            color. If a character is not defined in the dictionary the default
            color is used.
        - croppers: List of cropper objects to be rendered.
        - border_ration: Ratio of the empty space at the border to the cell
            size
    """
    DEFAULT_COLOR = "#CCCCCC"

    def __init__(self, cell_size, colors, croppers, border_ratio=0.05):
        self.root = tkinter.Tk()
        self.root.title("gymcolab")

        self.croppers = sorted(croppers, key=lambda x: x.rows, reverse=True)
        width = ((sum(cropper.cols for cropper in croppers) +
                  len(croppers) - 1) * cell_size)
        height = max(cropper.rows for cropper in croppers) * cell_size

        self.canvas = tkinter.Canvas(
            self.root, width=width, height=height, bg="gray")
        self.canvas.pack()
        self.canvas_height = height
        self.canvas_widht = width
        self.cell_size = cell_size

        self.border_ratio = border_ratio
        self.colors = defaultdict(lambda: DEFAULT_COLOR)
        for key, value in colors.items():
            self.colors[ord(key)] = value

    def _init_render(self):
        """ Initialize the renderer and pop ups the window. Create each cell
        in each croppers. While doing so leaving a single cell sized gap
        between the cells of different croppers.
        Return:
            - List of cell for all croppers.
        """
        cell_list = []
        global_col = 0
        for cropper in self.croppers:
            rows = cropper.rows
            cols = cropper.cols

            b_w = int(self.cell_size*self.border_ratio)
            b_h = int(self.cell_size*self.border_ratio)

            cells = [self.canvas.create_rectangle(x*self.cell_size + b_w,
                                                  y*self.cell_size + b_h,
                                                  (x+1)*self.cell_size - b_w,
                                                  (y+1)*self.cell_size - b_h)
                     for x, y in product(range(global_col, cols + global_col),
                                         range(rows))]
            cell_list.append(cells)
            global_col += (1 + cropper.cols)
        return cell_list

    def __call__(self, board):
        """ Render the board using croppers.
            Raise:
                - Attrubute Error: If the renderer is not initialized using
                    <_init_render> function
        """
        try:
            self.cell_list
        except AttributeError:
            self.cell_list = self._init_render()

        for cropper, cells in zip(self.croppers, self.cell_list):
            cropped_board = cropper.crop(board).board
            for i, v in enumerate(cropped_board.flatten("F")):
                self.canvas.itemconfig(cells[i], fill=self.colors[v])
        self.root.update()
