import numpy as np
from numba import njit


def mezzo(img, settings, mode="uniform"):
    seed = settings["seed"]
    h, w = img.shape
    rng = np.random.default_rng(seed)

    if mode == "uniform":
        r_min, r_max = settings["range"]
        r_min /= 100
        r_max /= 100
        print(r_min, r_max)
        noise = rng.uniform(r_min, r_max, (h, w))
    elif mode == "gauss":
        loc = settings["location"] / 100
        std = settings["std"] / 200
        noise = rng.normal(loc, std, (h, w))
    elif mode == "beta":
        alpha = settings["alpha"] / 10
        beta = settings["beta"] / 10
        noise = rng.beta(alpha, beta, (h, w))

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
