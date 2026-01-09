# sierra24a.pxi

from libc.stdint cimport int32_t, uint8_t, uint16_t, uint32_t

def sierra24a(img, float diffusion_factor=1.0, bint serpentine=True):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]

    out = np.zeros((h, w), dtype=np.uint8)

    # signed int32 buffer for errors
    cdef int32_t[:, :] work_buf = np.array(img, dtype=np.int32)

    _sierra24a_core(work_buf, out, h, w, diffusion_factor, serpentine)

    return out.view(np.bool_)

cdef void _sierra24a_core(int32_t[:, :] img, uint8_t[:, :] out, int h, int w, float str_val, bint serpentine) noexcept nogil:
    cdef int y, x
    cdef int32_t old_val, new_val, error
    cdef int32_t threshold = 32768

    for y in range(h):
        if serpentine and (y % 2 == 0):
            for x in range(w - 1, -1, -1):
                old_val = img[y, x]
                if old_val >= threshold:
                    new_val = 65535
                    out[y, x] = 1
                else:
                    new_val = 0
                    out[y, x] = 0

                error = <int32_t>((old_val - new_val) * str_val)

                if x - 1 >= 0: # left
                    img[y, x - 1] += (error >> 1)

                if y + 1 < h: # down
                    img[y + 1, x] += (error >> 2)
                    if x + 1 < w: # down right
                        img[y + 1, x + 1] += (error >> 2)

        else:
            for x in range(w):
                old_val = img[y, x]
                if old_val >= threshold:
                    new_val = 65535
                    out[y, x] = 1
                else:
                    new_val = 0
                    out[y, x] = 0

                error = <int32_t>((old_val - new_val) * str_val)


                if x + 1 < w: # right
                    img[y, x + 1] += (error >> 1)

                if y + 1 < h: # down
                    img[y + 1, x] += (error >> 2)
                    if x - 1 >= 0: # down left
                        img[y + 1, x - 1] += (error >> 2)
