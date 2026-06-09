# nakano.pxi
from libc.stdint cimport int32_t, uint8_t, uint16_t

def nakano(img_u16, double str_value, double hysteresis_c, bint serpentine):
    cdef int h = img_u16.shape[0]
    cdef int w = img_u16.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef int32_t[:, :] img = np.array(img_u16, dtype=np.int32)
    _nakano_core(img, out, h, w, str_value, hysteresis_c, serpentine)
    return out.view(np.bool_)

cdef void _nakano_core(
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
    cdef bint reverse
    # precomputed constants for the maximum uint16 value
    cdef int32_t VAL_7 = 28671  # (65535 * 7) >> 4
    cdef int32_t VAL_5 = 20479  # (65535 * 5) >> 4
    cdef int32_t VAL_3 = 12287  # (65535 * 3) >> 4
    cdef int32_t VAL_1 = 4095   # 65535 >> 4

    for y in range(h):
        reverse = serpentine and (y % 2 == 0)
        for x in range(w):
            actual_x = (w - 1 - x) if reverse else x
            old_value = img[y, actual_x]
            hysteresis = 0
            if hysteresis_c > 0:
                # using rotated Floyd-Steinberg kernel
                if not reverse: # noqua: SIM102
                    # current row
                    if actual_x - 1 >= 0:  # noqa: SIM102
                        if out[y, actual_x - 1]:
                            hysteresis += VAL_7  # x - 1
                    # row above
                    if y - 1 >= 0:
                        if out[y - 1, actual_x]:
                            hysteresis += VAL_5  # current x
                        if actual_x - 1 >= 0:  # noqa: SIM102
                            if out[y - 1, actual_x - 1]:
                                hysteresis += VAL_1  # x - 1
                        if actual_x + 1 < w:  # noqa: SIM102
                            if out[y - 1, actual_x + 1]:
                                hysteresis += VAL_3  # x + 1
                else:
                    if actual_x + 1 < w:  # noqa: SIM102
                        if out[y, actual_x + 1]:
                            hysteresis += VAL_7  # x - 1
                    # row above
                    if y - 1 >= 0:
                        if out[y - 1, actual_x]:
                            hysteresis += VAL_5  # current x
                        if actual_x + 1 < w:  # noqa: SIM102
                            if out[y - 1, actual_x + 1]:
                                hysteresis += VAL_1  # x - 1
                        if actual_x - 1 >= 0:  # noqa: SIM102
                            if out[y - 1, actual_x - 1]:
                                hysteresis += VAL_3  # x + 1
            hysteresis = <int32_t>(hysteresis * hysteresis_c)
            if old_value + hysteresis >= THRESHOLD:
                new_value = 65535
                out[y, actual_x] = 1
            else:
                new_value = 0
                out[y, actual_x] = 0
            error = <int32_t>((old_value - new_value) * str_value)
            # as the sum of the kernel is 64, bitshifts were used. this shaved about 0.1s from the execution. i'm sorry if someone ever reads the following:
            if not reverse:
                # current row
                if actual_x + 2 < w:
                    img[y, actual_x + 2] += (error * 6) >> 6  # x + 2
                if actual_x + 3 < w:
                    img[y, actual_x + 3] += (error * 4) >> 6  # x + 3
                # row + 1
                if y + 1 < h:
                    if actual_x - 2 >= 0:
                        img[y + 1, actual_x - 2] += (error * 1) >> 6  # x - 2
                    if actual_x - 1 >= 0:
                        img[y + 1, actual_x - 1] += (error * 6) >> 6  # x - 1
                    if actual_x + 2 < w:
                        img[y + 1, actual_x + 2] += (error * 5) >> 6  # x + 2
                    if actual_x + 3 < w:
                        img[y + 1, actual_x + 3] += (error * 3) >> 6  # x + 3
                # row + 2
                if y + 2 < h:
                    if actual_x - 1 >= 0:
                        img[y + 2, actual_x - 1] += (error * 4) >> 6  # x - 1
                    # no checks, x is directly bellow
                    img[y + 2, actual_x] += (error * 7) >> 6
                    if actual_x + 1 < w:
                        img[y + 2, actual_x + 1] += (error * 3) >> 6  # x + 1
                    if actual_x + 2 < w:
                        img[y + 2, actual_x + 2] += (error * 5) >> 6  # x + 2
                    if actual_x + 3 < w:
                        img[y + 2, actual_x + 3] += (error * 3) >> 6  # x + 3
                # row + 3
                if y + 3 < h:
                    if actual_x - 1 >= 0:
                        img[y + 3, actual_x - 1] += (error * 3) >> 6  # x - 1
                    # no checks, same reason
                    img[y + 3, actual_x] += (error * 5) >> 6
                    if actual_x + 1 < w:
                        img[y + 3, actual_x + 1] += (error * 3) >> 6  # x + 1
                    if actual_x + 2 < w:
                        img[y + 3, actual_x + 2] += (error * 4) >> 6  # x + 2
                    if actual_x + 3 < w:
                        img[y + 3, actual_x + 3] += (error * 2) >> 6  # x + 3

            else:
                # current row
                if actual_x - 2 >= 0:
                    img[y, actual_x - 2] += (error * 6) >> 6  # x + 2
                if actual_x - 3 >= 0:
                    img[y, actual_x - 3] += (error * 4) >> 6  # x + 3
                # row + 1
                if y + 1 < h:
                    if actual_x + 2 < w:
                        img[y + 1, actual_x + 2] += (error * 1) >> 6  # x - 2
                    if actual_x + 1 < w:
                        img[y + 1, actual_x + 1] += (error * 6) >> 6  # x - 1
                    if actual_x - 2 >= 0:
                        img[y + 1, actual_x - 2] += (error * 5) >> 6  # x + 2
                    if actual_x - 3 >= 0:
                        img[y + 1, actual_x - 3] += (error * 3) >> 6  # x + 3
                # row + 2
                if y + 2 < h:
                    if actual_x + 1 < w:
                        img[y + 2, actual_x + 1] += (error * 4) >> 6  # x - 1
                    # no checks, x is directly bellow
                    img[y + 2, actual_x] += (error * 7) >> 6
                    if actual_x - 1 >= 0:
                        img[y + 2, actual_x - 1] += (error * 3) >> 6  # x + 1
                    if actual_x - 2 < w:
                        img[y + 2, actual_x - 2] += (error * 5) >> 6  # x + 2
                    if actual_x - 3 < w:
                        img[y + 2, actual_x - 3] += (error * 3) >> 6  # x + 3
                # row + 3
                if y + 3 < h:
                    if actual_x + 1 < w:
                        img[y + 3, actual_x + 1] += (error * 3) >> 6  # x - 1
                    # no checks, same reason
                    img[y + 3, actual_x] += (error * 5) >> 6
                    if actual_x - 1 >= 0:
                      img[y + 3, actual_x - 1] += (error * 3) >> 6  # x + 1
                    if actual_x - 2 >= 0:
                      img[y + 3, actual_x - 2] += (error * 4) >> 6  # x + 2
                    if actual_x - 3 >= 0:
                      img[y + 3, actual_x - 3] += (error * 2) >> 6  # x + 3
