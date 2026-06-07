# ordered_dither.pxi
from libc.stdint cimport uint8_t

def ordered_dither(img, matrix):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef uint8_t[:, :] img_buf = np.array(img, dtype=np.uint8)
    cdef uint8_t[:, :] matrix_buf = np.array(matrix, dtype=np.uint8)
    cdef int n = matrix.shape[0]
    cdef int m = matrix.shape[1]
    _ordered_dither_core(img_buf, matrix_buf, out, h, w, n, m)
    return out.view(np.bool_)

cdef void _ordered_dither_core(uint8_t[:, :] img, uint8_t[:, :] matrix, uint8_t[:, :] out, int h, int w, int n, int m) noexcept nogil:
    cdef int y, x, i, j
    cdef uint8_t pixel
    for y in prange(h):
        for x in range(w):
            pixel = img[y, x]
            j = y % n
            if not (pixel == 0 or pixel == 1):
                i = x % m
                if matrix[j, i] > pixel:
                    out[y, x] = 0
                else:
                    out[y, x] = 1
