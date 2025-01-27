import numpy as np
from numba import njit

"""
I've tried improving this function in numerous ways a it is purely aesthetic and does nothing important. I've tried using prange, though it seems that the overhead of parallelisation is more important than the actual improvement achieved by it. Also tried assigning x,y as a whole, whick gave slightly worse results. The static version is also about 10% slower that the njitted one.
"""

@njit
def style_image(img, black, white):
    h, w = img.shape
    output_img = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            if img[y, x] == 0:
                output_img[y, x, 0] = black[0]
                output_img[y, x, 1] = black[1]
                output_img[y, x, 2] = black[2]
            else:
                output_img[y, x, 0] = white[0]
                output_img[y, x, 1] = white[1]
                output_img[y, x, 2] = white[2]
    return output_img
