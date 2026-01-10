# normalize.pxi
from libc.stdint cimport uint8_t, uint16_t
import numpy as np
cimport numpy as cnp
from cython.parallel import prange

import numpy as np
cimport numpy as np
from libc.stdint cimport uint8_t, uint16_t
import cython

def normalize(img, bint lut=False):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    cdef uint8_t min_v8, max_v8
    cdef uint16_t min_v16, max_v16

    is_u8 = img.dtype == np.uint8

    if is_u8:
        min_v8 = 255
        max_v8 = 0
        _find_min_max_u8(img, h, w, &min_v8, &max_v8)

        # if it spans the full range, normalizing would do nothing so just return back the image. min_v == max_v would result in divison by zero so return the image too.
        if (min_v8 == 0 and max_v8 == 255) or min_v8 == max_v8:
            return img

        if lut:
            _normalize_u8_lut(img, h, w, min_v8, max_v8)
        else:
            _normalize_u8(img, h, w, min_v8, max_v8)

    else:
        min_v16 = 65535
        max_v16 = 0
        _find_min_max_u16(img, h, w, &min_v16, &max_v16)

        # if it spans the full range, normalizing would do nothing so just return back the image. min_v == max_v would result in divison by zero so return the image too.
        if (min_v16 == 0 and max_v16 == 65535) or min_v16 == max_v16:
            return img

        _normalize_u16(img, h, w, min_v16, max_v16)

    return img

cdef void _find_min_max_u8(uint8_t[:, :] img, int h, int w, uint8_t* min_val, uint8_t* max_val) noexcept nogil:
    cdef int y, x
    cdef uint8_t val

    # local copies
    cdef uint8_t cur_min = min_val[0]
    cdef uint8_t cur_max = max_val[0]

    for y in range(h):
        for x in range(w):
            val = img[y, x]
            if val < cur_min:
                cur_min = val
            if val > cur_max:
                cur_max = val

    # write back to pointers
    min_val[0] = cur_min
    max_val[0] = cur_max

cdef void _find_min_max_u16(uint16_t[:, :] img, int h, int w, uint16_t* min_val, uint16_t* max_val) noexcept nogil:
    cdef int y, x
    cdef uint16_t val

    # local copies
    cdef uint16_t cur_min = min_val[0]
    cdef uint16_t cur_max = max_val[0]

    for y in range(h):
        for x in range(w):
            val = img[y, x]
            if val < cur_min:
                cur_min = val
            if val > cur_max:
                cur_max = val

    # write back to pointers
    min_val[0] = cur_min
    max_val[0] = cur_max

cdef void _normalize_u8_lut(uint8_t[:, :] img, int h, int w, uint8_t min_v, uint8_t max_v) noexcept nogil:
    cdef int y, x, v
    cdef uint8_t lut[256]
    # get the scale factor
    cdef float scale = 255.0 / <float>(max_v - min_v)

    # build a LUT to check if its faster
    for v in range(256):
        if v <= min_v:
            lut[v] = 0
        elif v >= max_v:
            lut[v] = 255
        else:
            lut[v] = <uint8_t>((<float>v - <float>min_v) * scale)

    # aplly the LUT
    for y in prange(h, schedule='static'):
        for x in range(w):
            # using the value of the pixel as an index in the LUT
            img[y, x] = lut[img[y, x]]

cdef void _normalize_u8(uint8_t[:, :] img, int h, int w, uint8_t min_v, uint8_t max_v) noexcept nogil:
    cdef int y, x
    # get the scale factor
    cdef float scale = 255.0 / <float>(max_v - min_v)

    for y in prange(h, schedule='static'):
        for x in range(w):
            # nomalize using (x - min) * (range / (max - min))
            img[y, x] = <uint8_t>((<float>img[y, x] - <float>min_v) * scale)

cdef void _normalize_u16(uint16_t[:, :] img, int h, int w, uint16_t min_v, uint16_t max_v) noexcept nogil:
    cdef int y, x
    # get the scale factor
    cdef float scale = 65535.0 / <float>(max_v - min_v)

    for y in prange(h, schedule='static'):
        for x in range(w):
            # nomalize using (x - min) * (range / (max - min))
            img[y, x] = <uint16_t>((<float>img[y, x] - <float>min_v) * scale)
