# style_alpha.pxi

def style_alpha(
    uint8_t[:, :] img,
    uint8_t[:, :] alpha_img,
    uint8_t[:] black,
    uint8_t[:] white,
    uint8_t[:] alpha
):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]

    cdef uint8_t[:, :, :] out = np.empty((h, w, 3), dtype=np.uint8)

    cdef int b0 = black[0], b1 = black[1], b2 = black[2]
    cdef int w0 = white[0], w1 = white[1], w2 = white[2]
    cdef int a0 = alpha[0], a1 = alpha[1], a2 = alpha[2]

    cdef int y, x, a_val, a_inv, c_r, c_g, c_b
    cdef int tmp

    for y in prange(h, schedule='static', nogil=True):
        for x in range(w):
            a_val = <int>alpha_img[y, x]
            a_inv = 255 - a_val

            if img[y, x]:
                c_r, c_g, c_b = w0, w1, w2
            else:
                c_r, c_g, c_b = b0, b1, b2

            # Red
            tmp = c_r * a_val + a0 * a_inv
            out[y, x, 0] = <uint8_t>((tmp + 1 + (tmp >> 8)) >> 8)
            # Green
            tmp = c_g * a_val + a1 * a_inv
            out[y, x, 1] = <uint8_t>((tmp + 1 + (tmp >> 8)) >> 8)
            # Blue
            tmp = c_b * a_val + a2 * a_inv
            out[y, x, 2] = <uint8_t>((tmp + 1 + (tmp >> 8)) >> 8)

    return np.asarray(out)
