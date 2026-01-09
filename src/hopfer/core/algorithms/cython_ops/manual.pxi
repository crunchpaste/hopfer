# manual.pxi

def manual(img, double rf, double gf, double bf, bint out_8bit=False):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    is_u8 = img.dtype == np.uint8

    if out_8bit:
        out_u8 = np.empty((h, w), dtype=np.uint8)
        if is_u8:
            _manual_u8_u8(img, out_u8, rf, gf, bf)
        else:
            _manual_u16_u8(img, out_u8, rf, gf, bf)
        return out_u8
    else:
        out_u16 = np.empty((h, w), dtype=np.uint16)
        if is_u8:
            _manual_u8_u16(img, out_u16, rf, gf, bf)
        else:
            _manual_u16_u16(img, out_u16, rf, gf, bf)
        return out_u16

cdef void _manual_u16_u16(uint16_t[:, :, :] img, uint16_t[:, :] out, double rf, double gf, double bf) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef double val
    cdef uint16_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            val = rf * r + gf * g + bf * b

            if val > 65535.0: val = 65535.0
            elif val < 0.0: val = 0.0

            out[y, x] = <uint16_t>val

cdef void _manual_u8_u8(uint8_t[:, :, :] img, uint8_t[:, :] out, double rf, double gf, double bf) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef double val
    cdef uint8_t r, g, b

    for y in prange(h, schedule='static'):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            val = rf * r + gf * g + bf * b

            if val > 255.0: val = 255.0
            elif val < 0.0: val = 0.0

            out[y, x] = <uint8_t>val

cdef void _manual_u16_u8(uint16_t[:, :, :] img, uint8_t[:, :] out, double rf, double gf, double bf) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef double val

    for y in prange(h, schedule='static'):
        for x in range(w):
            val = (rf * img[y, x, 0] + gf * img[y, x, 1] + bf * img[y, x, 2]) / 256.0

            if val > 255.0: val = 255.0
            elif val < 0.0: val = 0.0

            out[y, x] = <uint8_t>val

cdef void _manual_u8_u16(uint8_t[:, :, :] img, uint16_t[:, :] out, double rf, double gf, double bf) noexcept nogil:
    cdef int y, x, h = img.shape[0], w = img.shape[1]
    cdef double val

    for y in prange(h, schedule='static'):
        for x in range(w):
            val = (rf * img[y, x, 0] + gf * img[y, x, 1] + bf * img[y, x, 2]) * 256.0

            if val > 65535.0: val = 65535.0
            elif val < 0.0: val = 0.0

            out[y, x] = <uint16_t>val
