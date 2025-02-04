from .static import compare
import numpy as np

def mezzo(img, settings):
    seed = settings["seed"]
    h, w = img.shape
    rng = np.random.default_rng(seed)
    noise = rng.random((h,w))
    img = compare(img, noise, h, w)
    return img
