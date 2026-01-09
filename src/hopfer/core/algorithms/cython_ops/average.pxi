# average.pxi

def average(img, bint out_8bit=False):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    is_u8 = img.dtype == np.uint8

    if out_8bit:
        out_u8 = np.empty((h, w), dtype=np.uint8)
        if is_u8:
            _average_u8_u8(img, out_u8)
        else:
            _average_u16_u8(img, out_u8)
        return out_u8
    else:
        out_u16 = np.empty((h, w), dtype=np.uint16)
        if is_u8:
            _average_u8_u16(img, out_u16)
        else:
            _average_u16_u16(img, out_u16)
        return out_u16

cdef void _average_u16_u16(uint16_t[:, :, :] img, uint16_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint32_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint16_t>((r + g + b + 1) // 3)

cdef void _average_u8_u8(uint8_t[:, :, :] img, uint8_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint16_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint8_t>((r + g + b + 1) // 3)

cdef void _average_u16_u8(uint16_t[:, :, :] img, uint8_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint32_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint8_t>(((r + g + b + 1) // 3) >> 8)

cdef void _average_u8_u16(uint8_t[:, :, :] img, uint16_t[:, :] out) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef uint16_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]
            out[y, x] = <uint16_t>(((r + g + b + 1) // 3) << 8)
