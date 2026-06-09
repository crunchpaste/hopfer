# levien.pxi
from libc.stdint cimport int32_t, uint8_t, uint16_t

def levien(img_u16, double str_value, double hysteresis_c, bint serpentine):
    cdef int h = img_u16.shape[0]
    cdef int w = img_u16.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef int32_t[:, :] img = np.array(img_u16, dtype=np.int32)
    _levien_core(img, out, h, w, str_value, hysteresis_c, serpentine)
    return out.view(np.bool_)

cdef void _levien_core(
    int32_t[:, :] img,
    uint8_t[:, :] out,
    int h, int w,
    double str_value,
    double hysteresis_c,
    bint serpentine
) noexcept nogil:
    cdef int y, x, actual_x
    cdef int32_t old_value, new_value, error, hysteresis
    cdef int32_t THRESHOLD = 32768
    cdef int32_t HVAL = 32767  # this is the value of the hysteresis per pixel
    cdef bint reverse

    for y in range(h):
        reverse = serpentine and (y % 2 == 0)
        for x in range(w):
            actual_x = (w - 1 - x) if reverse else x
            old_value = img[y, actual_x]
            hysteresis = 0
            # get the hysteresis value here. if hysteresis is 0 there is absolutely no need to hit these indeces up and waste time.
            if hysteresis_c != 0:
                if not reverse:
                    # current row
                    if actual_x - 1 >= 0 and out[y, actual_x - 1]:
                        hysteresis += HVAL  # x - 1
                    # row above
                    if y - 1 >= 0 and out[y - 1, actual_x]:
                        hysteresis += HVAL  # current x
                else:
                    # current row
                    if actual_x + 1 < w and out[y, actual_x + 1]:
                        hysteresis += HVAL  # x - 1
                    # row above
                    if y - 1 >= 0 and out[y - 1, actual_x]:
                        hysteresis += HVAL  # current x

            hysteresis = <int32_t>(hysteresis * hysteresis_c)
            if old_value + hysteresis >= THRESHOLD:
                new_value = 65535
                out[y, actual_x] = 1
            else:
                new_value = 0
                out[y, actual_x] = 0
            error = <int32_t>((old_value - new_value) * str_value)
            # as the sum of the kernel is 2, bitshifts were used.
            if not reverse:
                # current row
                if actual_x + 1 < w:
                    img[y, actual_x + 1] += error >> 1  # x + 1
                # row bellow
                if y + 1 < h:
                    img[y + 1, actual_x] += error >> 1
            else:
                # current row
                if actual_x - 1 >= 0:
                    img[y, actual_x - 1] += error >> 1  # x + 1
                # row bellow
                if y + 1 < h:
                    img[y + 1, actual_x] += error >> 1
