# ostromoukhov.pxi
from libc.stdint cimport int32_t, uint8_t, uint16_t

def ostromoukhov(img_u16, coeff_array, double str_value):
    cdef int h = img_u16.shape[0]
    cdef int w = img_u16.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    # temporary promotion to int32 so that error could accumulate
    cdef int32_t[:, :] img = np.array(img_u16, dtype=np.int32)
    cdef double[:, :] coeff_buf = np.array(coeff_array, dtype=np.float64)
    _ostromoukhov_core(img, coeff_buf, out, h, w, str_value)
    return out.view(np.bool_)

cdef void _ostromoukhov_core(
    int32_t[:, :] img,
    double[:, :] coeff_array,
    uint8_t[:, :] out,
    int h, int w,
    double str_value
) noexcept nogil:
    cdef int y, x, coeff_idx
    cdef int32_t old_value, new_value
    cdef double error
    cdef int32_t THRESHOLD = 32768

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255
            if old_value >= THRESHOLD:
                new_value = 65535
                out[y, x] = 1
            else:
                new_value = 0
                out[y, x] = 0
            error = (old_value - new_value) * str_value
            if x + 1 < w:
                img[y, x + 1] += <int32_t>(error * coeff_array[coeff_idx, 0])
            if x - 1 >= 0 and y + 1 < h:
                img[y + 1, x - 1] += <int32_t>(error * coeff_array[coeff_idx, 1])
            if y + 1 < h:
                img[y + 1, x] += <int32_t>(error * coeff_array[coeff_idx, 2])
