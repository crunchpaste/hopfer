# luma.pxi

def luma(img, bool out_8bit=False):
    # Rec. 601 coefficients
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    is_u8 = img.dtype == np.uint8

    if out_8bit:
        out_u8 = np.empty((h, w), dtype=np.uint8)
        if is_u8:
            _luma_u8_u8(img, out_u8)
        else:
            _luma_u16_u8(img, out_u8)
        return out_u8
    else:
        out_u16 = np.empty((h, w), dtype=np.uint16)
        if is_u8:
            _luma_u8_u16(img, out_u16)
        else:
            _luma_u16_u16(img, out_u16)
        return out_u16

cdef void _luma_u16_u16(uint16_t[:, :, :] img, uint16_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint16_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint16_t>(0.299 * r + 0.587 * g + 0.114 * b + 0.5)

cdef void _luma_u8_u8(uint8_t[:, :, :] img, uint8_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint8_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint8_t>(0.299 * r + 0.587 * g + 0.114 * b + 0.5)

cdef void _luma_u16_u8(uint16_t[:, :, :] img, uint8_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint16_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint8_t>((<uint16_t>(0.299 * r + 0.587 * g + 0.114 * b + 0.5)) >> 8)

cdef void _luma_u8_u16(uint8_t[:, :, :] img, uint16_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint8_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint16_t>(0.299 * r + 0.587 * g + 0.114 * b + 0.5) << 8
