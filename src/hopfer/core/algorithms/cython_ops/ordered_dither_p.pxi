# ordered_dither_p.pxi
from libc.stdint cimport uint8_t
from libc.stdlib cimport rand, RAND_MAX
from cython.parallel cimport prange

def ordered_dither_p(img, matrix, double pert=0.1):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef uint8_t[:, :] img_buf = np.array(img, dtype=np.uint8)
    cdef uint8_t[:, :] matrix_buf = np.array(matrix, dtype=np.uint8)
    cdef int n = matrix.shape[0]
    cdef int m = matrix.shape[1]
    _ordered_dither_p_core(img_buf, matrix_buf, out, h, w, n, m, pert)
    return out.view(np.bool_)

cdef void _ordered_dither_p_core(
    uint8_t[:, :] img,
    uint8_t[:, :] matrix,
    uint8_t[:, :] out,
    int h, int w, int n, int m,
    double pert
) noexcept nogil:
    cdef int y, x, i, j
    cdef uint8_t pixel
    cdef double threshold

    for y in prange(h):
        for x in range(w):
            pixel = img[y, x]
            j = y % n
            if not (pixel == 0 or pixel == 1):
                i = x % m
                # uniform in [-pert, +pert], scaled to uint8 range
                threshold = matrix[j, i] + (<double>rand() / RAND_MAX * 2.0 - 1.0) * pert * 255.0
                if threshold > pixel:
                    out[y, x] = 0
                else:
                    out[y, x] = 1
