import numpy as np
from numba import njit

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

@njit(cache=True)
def thresh(img, threshold_value):
    # As simple as it gets :)
    # Slightly (about 15%) improves performace when in njit. Unfortunately slightly slower in static.
    t = threshold_value - 0.5
    img = np.rint(img + t)
    return img
