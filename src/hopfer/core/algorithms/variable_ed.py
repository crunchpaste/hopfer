import numpy as np
from numba import njit

from .ved_data import OSTROMOUKHOV_COEFFN, ZF_COEFFN, ZF_PERT


def variable_ed(img, algorithm, settings):
    str = settings["diffusion_factor"]
    serpentine = settings["serpentine"]
    # noise = settings["noise"]
    noise = False
    if noise:
        noise_array = np.random.random((20, img.shape[1])).astype(np.int16)
        img = np.vstack((noise_array, img))

    if algorithm == "Ostromoukhov":
        if serpentine:
            output_img = ostromoukhov_s(img, OSTROMOUKHOV_COEFFN, str)
        else:
            output_img = ostromoukhov_s(img, OSTROMOUKHOV_COEFFN, str)
    elif algorithm == "Zhou-Fang":
        if serpentine:
            output_img = zhou_fang_s(img, ZF_COEFFN, ZF_PERT, str)
        else:
            output_img = zhou_fang(img, ZF_COEFFN, ZF_PERT, str)
    else:
        # Default to Zhou-Fang serpentine
        output_img = zhou_fang_s(img, ZF_COEFFN, ZF_PERT, str)
    if noise:
        output_img = output_img[20:, :]

    return output_img


@njit
def ostromoukhov(img, coeff_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value)
            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]

    return img


@njit
def ostromoukhov_s(img_u16, coeff_array, str_value):
    h, w = img_u16.shape

    # promote to int32 for error accumulation
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768

    for y in range(h):
        # serpentine direction
        if (y & 1) == 0:
            x_start = 0
            x_end = w
            x_step = 1
        else:
            x_start = w - 1
            x_end = -1
            x_step = -1

        x = x_start
        while x != x_end:
            old_value = img[y, x]

            # map to 0–255 coefficient table
            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            coeff_values = coeff_array[coeff_idx]

            if old_value >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0
                output[y, x] = False

            error = (old_value - new_value) * str_value

            # diffuse error relative to scan direction
            nx = x + x_step
            if 0 <= nx < w:
                img[y, nx] += np.int32(error * coeff_values[0])

            ny = y + 1
            if ny < h:
                bx = x - x_step
                if 0 <= bx < w:
                    img[ny, bx] += np.int32(error * coeff_values[1])
                img[ny, x] += np.int32(error * coeff_values[2])

            x += x_step

    return output


@njit
def zhou_fang(img, coeff_array, pert_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            pert = np.random.uniform(0, 0.5)
            pert_mod = pert * pert_array[coeff_idx]
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value + pert_mod)
            img[y, x] = new_value
            error = (old_value - new_value) * str
            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]
    return img


@njit
def zhou_fang_s(img, coeff_array, pert_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            pert = np.random.uniform(0, 0.5)
            pert_mod = pert * pert_array[coeff_idx]
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value + pert_mod)
            img[y, x] = new_value
            error = (old_value - new_value) * str
            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]
        img = np.fliplr(img)

    if h % 2 != 0:
        img = np.fliplr(img)
    return img
