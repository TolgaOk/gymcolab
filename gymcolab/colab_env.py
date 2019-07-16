""" Abstract class for Gym Colab environments. Include commom utilities.
"""
from itertools import chain
from gym import spaces
import numpy as np
from pycolab import cropping
from pycolab.rendering import ObservationToFeatureArray


class ColabEnv(gym.Env):

    metadata = {
        "render.modes": ["plot", "gui", "console"],
        "obs.modes": ["onehot", "index", "cropped-map"]
    }

    def __init__(self,
                 game,
                 character_colors=None,
                 render_cropers=None,
                 observation_cropper=None):

        if render_cropers is None:
            self._render_cropers = [cropping.ObservationCropper()]

        if observation_cropper is None:
            self._observation_cropper = cropping.ObservationCropper()

        chars = set(game.things.keys()).union(game._backdrop.palette)

        # # We need to create observation and action spaces, we call
        # # <its_showtime> method and take the observation after cropping
        # #  it just to find out the depth.

        # observation, _, _ = game.its_showtime()
        # depth = len(observation.layers.keys())
        self.observation_space = spaces.Box(low=0, high=1, shape=(len(chars),
            self._observation_cropper.rows, self._observation_cropper.cols))

        

class ObservaionToIndex():
    pass


class OnbservationToOnehot():
    pass


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
   class Observation:
        def __init__(self, game):
            self.characters = list(chain(game.things.keys(),
                                         list(game.backdrop.palette)))
            self.row, self.col = game.rows, game.cols
            self._game = game

        def to_map(self, board):
            chr_indx = np.array([ord(char) for char in self.characters])
            feature_map = np.expand_dims(
                board, 0) == chr_indx.reshape(-1, 1, 1)
            return feature_map

        def to_onehot(self, row, col):
            indexes = np.arange(self.row * self.col)
            return (indexes == ((row * self.col) + col)).astype("float32")

        def to_cropped_map(self, board, kernel_size, row, col):
            board_h, board_w = board.shape
            chr_indx = np.array([ord(char) for char in self.characters])
            kernel = np.zeros((len(chr_indx), kernel_size,
                               kernel_size), dtype="float32")

            x_lower = min(0, col - kernel_size//2)
            y_lower = min(0, row - kernel_size//2)
            x_upper = max(board_w, col + (kernel_size - kernel_size//2))
            y_upper = max(board_h, row + (kernel_size - kernel_size//2))

            kernel_board = board[y_lower:y_upper, x_lower:x_upper]
            kernel_board = np.expand_dims(kernel_board, 0)

            feature_map = kernel_board == chr_indx.reshape(-1, 1, 1)

            kernel_offset_x_lower = x_lower - (col - kernel_size//2)
            kernel_offset_y_lower = y_lower - (row - kernel_size//2)
            kernel_offset_x_upper = col + \
                (kernel_size - kernel_size//2) - x_upper
            kernel_offset_y_upper = row + \
                (kernel_size - kernel_size//2) - y_upper

            kernel[kernel_offset_x_lower:kernel_offset_x_upper,
                   kernel_offset_y_lower:kernel_offset_y_upper] = feature_map
            return kernel

        def get_map_observation_space(self):
            return spaces.Box(low=0, high=1,
                              shape=(len(self.characters),
                                     self.row, self.col),
                              dtype=np.float32)

        def get_cropped_map_observation_space(self, kernel_size):
            return spaces.Box(low=0, high=1,
                              shape=(len(self.characters),
                                     kernel_size, kernel_size))

        def get_onehot_observation_space(self):
            spaces.Box(low=0, high=1, shape=(self.row*self.col))
