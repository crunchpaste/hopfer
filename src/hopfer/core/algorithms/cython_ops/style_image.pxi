# style_image.pxi

def style_image(uint8_t[:, :] img, uint8_t[:] black, uint8_t[:] white):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]

    cdef uint8_t[:, :, :] out = np.empty((h, w, 3), dtype=np.uint8)

    cdef uint8_t b0 = black[0], b1 = black[1], b2 = black[2]
    cdef uint8_t w0 = white[0], w1 = white[1], w2 = white[2]

    cdef int y, x

    for y in prange(h, schedule='static', nogil=True):
        for x in range(w):
            if img[y, x]:
                out[y, x, 0] = w0
                out[y, x, 1] = w1
                out[y, x, 2] = w2
            else:
                out[y, x, 0] = b0
                out[y, x, 1] = b1
                out[y, x, 2] = b2

    return np.asarray(out)
