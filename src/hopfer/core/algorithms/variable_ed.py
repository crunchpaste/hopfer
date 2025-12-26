import numpy as np
from numba import njit

from .ved_data import OSTROMOUKHOV_COEFFN, ZF_COEFFN, ZF_PERT


def variable_ed(img, algorithm, settings):
    str = settings["diffusion_factor"] / 100
    serpentine = settings["serpentine"]
    noise = settings["noise"]
    if noise:
        noise_array = np.random.random((20, img.shape[1])).astype(np.float32)
        img = np.vstack((noise_array, img))

    if algorithm == "Ostromoukhov":
        if serpentine:
            output_img = ostromoukhov_s(img, OSTROMOUKHOV_COEFFN, str)
        else:
            output_img = ostromoukhov(img, OSTROMOUKHOV_COEFFN, str)
    if algorithm == "Zhou-Fang":
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
def ostromoukhov_s(img, coeff_array, str):
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

        img = np.fliplr(img)

    if h % 2 != 0:
        img = np.fliplr(img)
    return img


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
