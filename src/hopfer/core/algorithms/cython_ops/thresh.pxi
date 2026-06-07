# thresh.pxi

from libc.stdint cimport uint8_t

def thresh(img, float threshold_value=0.5):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef uint8_t[:, :] work_buf = np.array(img, dtype=np.uint8)
    _thresh_core(work_buf, out, h, w, threshold_value)
    return out.view(np.bool_)

cdef void _thresh_core(uint8_t[:, :] img, uint8_t[:, :] out, int h, int w, float threshold_value) noexcept nogil:
    cdef int y, x
    cdef float thresh_v = threshold_value * 255
    for y in prange(h, schedule='static'):
        for x in range(w):
            if img[y, x] > thresh_v:
                out[y, x] = 1
            else:
                out[y, x] = 0
