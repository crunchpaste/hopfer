# lightness.pxi
import numpy as np
cimport numpy as cnp
from cython.parallel import prange

def lightness(img, bint out_8bit=False):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    is_u8 = img.dtype == np.uint8

    if out_8bit:
        out_u8 = np.empty((h, w), dtype=np.uint8)
        if is_u8:
            _lightness_u8_u8(img, out_u8)
        else:
            _lightness_u16_u8(img, out_u8)
        return out_u8
    else:
        out_u16 = np.empty((h, w), dtype=np.uint16)
        if is_u8:
            _lightness_u8_u16(img, out_u16)
        else:
            _lightness_u16_u16(img, out_u16)
        return out_u16

cdef void _lightness_u16_u16(uint16_t[:, :, :] img, uint16_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint16_t r, g, b, mx, mn

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            mx = r
            if g > mx: mx = g
            if b > mx: mx = b

            mn = r
            if g < mn: mn = g
            if b < mn: mn = b

            out[y, x] = <uint16_t>((<uint32_t>mx + mn + 1) >> 1)

cdef void _lightness_u8_u8(uint8_t[:, :, :] img, uint8_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint8_t r, g, b, mx, mn

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            mx = r
            if g > mx: mx = g
            if b > mx: mx = b

            mn = r
            if g < mn: mn = g
            if b < mn: mn = b

            out[y, x] = <uint8_t>((<uint16_t>mx + mn + 1) >> 1)

cdef void _lightness_u16_u8(uint16_t[:, :, :] img, uint8_t[:, :] out) noexcept nogil:
    """16-bit to 8-bit. Shifted by 8 assuming standard u16 scaling."""
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint16_t r, g, b, mx, mn

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            mx = r
            if g > mx: mx = g
            if b > mx: mx = b

            mn = r
            if g < mn: mn = g
            if b < mn: mn = b

            out[y, x] = <uint8_t>(((<uint32_t>mx + mn + 1) >> 1) >> 8)

cdef void _lightness_u8_u16(uint8_t[:, :, :] img, uint16_t[:, :] out) noexcept nogil:
    """8-bit to 16-bit. Bit-shifted left by 8."""
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint8_t r, g, b, mx, mn

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            mx = r
            if g > mx: mx = g
            if b > mx: mx = b

            mn = r
            if g < mn: mn = g
            if b < mn: mn = b

            out[y, x] = <uint16_t>(((<uint16_t>mx + mn + 1) >> 1) << 8)
