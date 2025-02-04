import numpy as np
from numba import njit

def mezzo(img, settings, mode="uniform"):
    seed = settings["seed"]
    h, w = img.shape
    rng = np.random.default_rng(seed)
    if mode == "uniform":
        noise = rng.random((h, w))
    elif mode == "gauss":
        loc = settings["location"] / 100
        std = settings["location"] / 200
        std = np.min(std, np.min(loc, 1 - loc))
        print(std)
        noise = rng.normal((h, w), loc, std)

    img = compare(img, noise, h, w)
    return img

@njit
def compare(img, noise, h, w):
    # Doing it in this crude nested for loop seems to be a few times faster than using np.where
    for y in range(h):
        for x in range(w):
            if noise[y, x] > img[y, x]:
                img[y, x] = 0
            else:
                img[y, x] = 1
    return img
