import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True)
def luminance(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = 0.22 * r + 0.72 * g + 0.06 * b

    return output_img


@njit(parallel=True, cache=True)
def luma(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = 0.30 * r + 0.59 * g + 0.11 * b

    return output_img


@njit(parallel=True, cache=True)
def average(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = (r + g + b) / 3

    return output_img


@njit(parallel=True, cache=True)
def value(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            values = img[y, x, 0:3]
            output_img[y, x] = np.max(values)

    return output_img


@njit(parallel=True, cache=True)
def lightness(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            values = img[y, x, 0:3]
            max = np.max(values)
            min = np.min(values)
            output_img[y, x] = (max + min) * 0.5

    return output_img
