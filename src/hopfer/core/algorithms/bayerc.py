import numpy as np

from .static import ordered_dither, ordered_dither_p


def generate_halftone_matrix(size):
    matrix = np.zeros((size, size), dtype=int)
    center = (size - 1) / 2

    # the distance map
    distances = np.zeros((size, size))

    for i in range(size):
        for j in range(size):
            distances[i, j] = (i - center) ** 2 + (j - center) ** 2

    # sort the indices by distance from the center
    sorted_indices = np.argsort(distances, axis=None)

    # Assign values 0 to (size² - 1) based on distance ordering
    matrix.flat[sorted_indices] = np.arange(size**2)

    matrix = (matrix / np.max(matrix)) * 0.5

    # Generate negative version and stack into a 2x2 grid
    negative = np.fliplr(1 - matrix)

    # fmt: off
    stacked_matrix = np.block([[negative, matrix],
                               [matrix, negative]]).astype(np.float64)
    # fmt: on
    return stacked_matrix / np.max(stacked_matrix)


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
    perturbation = settings["perturbation"] / 200
    offset = settings["offset"] / 100
    matrix = generate_bayer_matrix(size, offset)
    if perturbation == 0:
        img = ordered_dither(img, matrix)
    else:
        img = ordered_dither_p(img, perturbation, matrix)
    return img


def clustered(img, settings):
    size = settings["size"] + 1
    # it proved massively hard to rotate a matrix by an arbitrary angle
    # and keep it tileable.
    # angle = settings["angle"]
    matrix = generate_halftone_matrix(size)
    img = ordered_dither(img, matrix)
    return img
