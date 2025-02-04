from .static import compare
import numpy as np

def mezzo(img, settings, mode="uniform"):
    seed = settings["seed"]
    h, w = img.shape
    rng = np.random.default_rng(seed)

    if mode == "uniform":
        noise = rng.random((h, w))
    elif mode == "gauss":
        loc = settings["location"] / 100
        std = settings["std"] / 200
        print(loc)
        print(std)
        noise = rng.normal(loc, std, (h, w))

    img = compare(img, noise, h, w)
    return img
