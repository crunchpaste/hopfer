# equalize.pxi
import numpy as np
cimport numpy as np
from libc.stdint cimport uint8_t, uint16_t, uint32_t
from cython.parallel import prange

def equalize(img):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]

    is_u8 = img.dtype == np.uint8

    if is_u8:
        _equalize_u8(img, h, w)
    else:
        _equalize_u16(img, h, w)

    return img

cdef void _equalize_u8(uint8_t[:, :] img, int h, int w) noexcept nogil:
    cdef int y, x, i
    cdef uint32_t hist[256]
    cdef uint8_t lut[256]
    cdef double total_pixels = <double>h * <double>w
    cdef uint32_t current_cdf = 0

    # create the histogram
    for i in range(256):
        hist[i] = 0

    # build it
    for y in range(h):
        for x in range(w):
            hist[img[y, x]] += 1

    # first non-zero
    i = 0
    while i < 255 and hist[i] == 0:
        i += 1

    cdef uint32_t min_cdf = hist[i]
    cdef double scale = 255.0 / (total_pixels - <double>min_cdf)

    # Build LUT from CDF
    for i in range(256):
        current_cdf += hist[i]
        if current_cdf <= min_cdf:
            lut[i] = 0
        else:
            lut[i] = <uint8_t>((<double>(current_cdf - min_cdf) * scale) + 0.5)

    # much faster when not in parallel
    for y in range(h):
        for x in range(w):
            img[y, x] = lut[img[y, x]]

cdef void _equalize_u16(uint16_t[:, :] img, int h, int w) noexcept nogil:
    cdef int y, x, i
    cdef uint32_t hist[65536]
    cdef uint16_t lut[65536]
    cdef double total_pixels = <double>h * <double>w
    cdef uint32_t current_cdf = 0

    # create the histogram
    for i in range(65536):
        hist[i] = 0

    # build it
    for y in range(h):
        for x in range(w):
            hist[img[y, x]] += 1

    # first non-zero
    i = 0
    while i < 65535 and hist[i] == 0:
        i += 1

    cdef uint32_t min_cdf = hist[i]
    cdef double scale = 65535.0 / (total_pixels - <double>min_cdf)

    # build lut from cdf
    for i in range(65536):
        current_cdf += hist[i]
        if current_cdf <= min_cdf:
            lut[i] = 0
        else:
            lut[i] = <uint16_t>((<double>(current_cdf - min_cdf) * scale) + 0.5)

    # LUT in parallel
    for y in prange(h, schedule='static'):
        for x in range(w):
            img[y, x] = lut[img[y, x]]
