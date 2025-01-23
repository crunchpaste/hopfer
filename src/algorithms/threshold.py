import numpy as np
from numba import njit

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

@njit
def thresh(img, threshold_value=.5):
    # Apply thresholding
    output_img = img.copy()
    h,w = img.shape
    # output = image.flatten()
    for i in range(h):
        for j in range(w):
            if output_img[i, j] > threshold_value:
                output_img[i, j] = 1
            else:
                output_img[i, j] = 0
    # thresholded_image = np.where(image >= threshold_value, 1, 0)

    return output_img
