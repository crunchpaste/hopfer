import numpy as np
from numba import njit, prange

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

def sauvola_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"] / 100
    k = settings["k_factor"] / 100
    return sauvola(img, block_size, dynamic_range, k)

@njit(parallel=True, cache=True, fastmath=True)
def sauvola(img, n=25, R=0.5, k=0.2):
    # Integral images should definitely be used at some point to speed this up
    h, w = img.shape
    w_half = n // 2  # Half size of the window for boundary checks

    output_img = np.zeros((h, w))

    for y in prange(h):
        # Boundary checks for the row
        y1 = max(0, y - w_half)  # Start of window
        y2 = min(h, y + w_half + 1)  # End of window

        for x in range(w):
            # marginally faster than the min max way
            x1 = x - w_half
            if x1 < 0:
                x1 = 0
            x2 = x + w_half
            if x2 > w:
                x2 = w

            # The block to check
            block = img[y1:y2, x1:x2]

            # Get the mean and the srd of the block
            mean = np.mean(block)
            std = np.std(block)

            # Apply the formula for the threshold explained lovely at
            # https://craftofcoding.wordpress.com/2021/10/06/thresholding-algorithms-sauvola-local/
            #
            threshold = mean * (1 + k * ((std / R) - 1))

            # Apply the thresholding
            if img[y, x] > threshold:
                output_img[y, x] = 1
            else:
                output_img[y, x] = 0

    return output_img
