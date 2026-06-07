# compare.pxi
from libc.stdint cimport uint8_t

def compare(img, noise):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef uint8_t[:, :] img_buf = np.array(img, dtype=np.uint8)
    cdef uint8_t[:, :] noise_buf = np.array(noise, dtype=np.uint8)
    _compare_core(img_buf, noise_buf, out, h, w)
    return out.view(np.bool_)

cdef void _compare_core(uint8_t[:, :] img, uint8_t[:, :] noise, uint8_t[:, :] out, int h, int w) noexcept nogil:
    cdef int y, x
    for y in prange(h, schedule='static'):
        for x in range(w):
            # Doing it in this crude nested for loop seems to be a few times faster than using np.where
            if noise[y, x] < img[y, x]:
                out[y, x] = 1
            else:
                out[y, x] = 0
