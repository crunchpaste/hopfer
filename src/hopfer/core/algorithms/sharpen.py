import numpy as np
from numba import njit, prange


@njit
def sharpen(image, str=1.0):
    str *= 0.1
    x = str + 1.0
    y = -str / 4

    # A classic sharpening kernel found on wiki
    kernel = np.array([[0, y, 0], [y, x, y], [0, y, 0]]).astype(np.float32)

    # Create a padded image to avoid out of bounds error
    padded_image = np.zeros((image.shape[0] + 2, image.shape[1] + 2)).astype(np.float32)
    padded_image[1:-1, 1:-1] = image

    sharpened = np.zeros((image.shape[0], image.shape[1]))

    for i in prange(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded_image[i : i + 3, j : j + 3]  # Extract the 3x3 region
            sharpened[i, j] = np.sum(region * kernel)  # Apply the kernel

    return sharpened
