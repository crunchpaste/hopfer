import numpy as np

from .static import bayer_dither


def generate_bayer_matrix(power, offset=0):
    n = 2 ** (power)

    bayer = np.array([[0, 2], [3, 1]])
    while bayer.shape[0] < n:
        bayer = np.concatenate(
            (
                np.concatenate((4 * bayer, 4 * bayer + 2), axis=1),
                np.concatenate((4 * bayer + 3, 4 * bayer + 1), axis=1),
            ),
            axis=0,
        )

    matrix = bayer / (bayer.shape[0] * bayer.shape[1])

    return np.clip(matrix - offset, 0, 1)


def bayer(img, settings):
    size = settings["size"]
    offset = settings["offset"] / 100
    matrix = generate_bayer_matrix(size, offset)
    img = bayer_dither(img, matrix)
    return img
