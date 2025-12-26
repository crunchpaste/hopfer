import numpy as np
from numba import njit


def edodf(img, algorithm, settings):
    str = settings["diffusion_factor"] / 100
    hysteresis_c = settings["hysteresis"] / 100
    serpentine = settings["serpentine"]
    noise = settings["noise"]
    if noise:
        noise_array = np.random.random((20, img.shape[1])).astype(np.float32)
        img = np.vstack((noise_array, img))

    if algorithm == "Levien":
        if serpentine:
            output_img = levien_s(img, hysteresis_c, str)
        else:
            output_img = levien(img, hysteresis_c, str)
    else:
        # Default to Zhou-Fang serpentine
        output_img = levien(img, hysteresis_c, str)

    if noise:
        output_img = output_img[20:, :]

    return output_img


@njit
def levien(img, hysteresis_c, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            hysteresis = 0

            if x - 1 >= 0:
                hysteresis += img[y, x - 1] * 0.5 * hysteresis_c
            if y - 1 >= 0:
                hysteresis += img[y - 1, x] * 0.5 * hysteresis_c

            if old_value + hysteresis > 0.5:
                new_value = 1
            else:
                new_value = 0

            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * 0.5
            if y + 1 < h:
                img[y + 1, x] += error * 0.5

    return img


@njit
def levien_s(img, hysteresis_c, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            hysteresis = 0

            if x - 1 >= 0:
                hysteresis += img[y, x - 1] * 0.5 * hysteresis_c
            if y - 1 >= 0:
                hysteresis += img[y - 1, x] * 0.5 * hysteresis_c

            if old_value + hysteresis > 0.5:
                new_value = 1
            else:
                new_value = 0

            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * 0.5
            if y + 1 < h:
                img[y + 1, x] += error * 0.5

        img = np.fliplr(img)

    if h % 2 != 0:
        img = np.fliplr(img)
    return img
