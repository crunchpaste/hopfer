# blur_helper.pxi
from libc.stdint cimport uint16_t
import numpy as np
cimport numpy as np
from cython.parallel import prange

def cast_f32_u16(float[:, :] src, uint16_t[:, :] dst):
    # casts an f32 array to u16 and clips.
    cdef int h = src.shape[0]
    cdef int w = src.shape[1]
    cdef int y, x
    cdef float val

    for y in prange(h, schedule='static', nogil=True):
        for x in range(w):
            val = src[y, x]

            if val > 65535.0:
                dst[y, x] = 65535
            elif val < 0.0:
                dst[y, x] = 0
            else:
                dst[y, x] = <uint16_t>(val + 0.5)
