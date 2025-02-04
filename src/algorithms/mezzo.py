import numpy as np
from numba import njit

def mezzo(img, settings):
    seed = settings["seed"]
    h, w = img.shape
    rng = np.random.default_rng(seed)
    noise = rng.random((h,w))
    img = compare(img, noise, h, w)
    return img

@njit
def compare(img, noise, h, w):
    for y in range(h):
        for x in range(w):
            if noise[y, x] > img[y, x]:
                img[y, x] = 0
            else:
                img[y, x] = 1
    return img
