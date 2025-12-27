# cython: boundscheck=False, wraparound=False, cdivision=True
import numpy as np
cimport numpy as cnp
from cython.parallel import prange

ctypedef fused floating:
    cnp.float32_t
    cnp.float64_t

def fast_to_uint8(floating[:, :, ::1] img_in):
    cdef int h = img_in.shape[0]
    cdef int w = img_in.shape[1]
    cdef int c = img_in.shape[2]
    cdef int y, x, i
    cdef float val

    cdef unsigned char[:, :, ::1] img_out = np.empty((h, w, c), dtype=np.uint8)

    with nogil:
        for y in prange(h, schedule='static', chunksize=64):
            for x in range(w):
                for i in range(c):
                    val = <float>img_in[y, x, i] * 255.0
                    if val > 255.0: val = 255.0
                    elif val < 0.0: val = 0.0
                    img_out[y, x, i] = <unsigned char>val

    return np.asarray(img_out)

def pack_to_qimage_buffer(floating[:, :, ::1] img, floating[:, :] alpha=None):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    cdef int c = img.shape[2]

    cdef int target_c = 4 if (alpha is not None or c == 4 or c == 2) else c

    cdef unsigned char[:, :, ::1] out = np.empty((h, w, target_c), dtype=np.uint8)

    cdef int x, y
    cdef float r, g, b, a, val

    with nogil:
        for y in prange(h, schedule='static'):
            for x in range(w):
                if alpha is not None:
                    a = <float>alpha[y, x] * 255.0
                elif c == 4:
                    a = <float>img[y, x, 3] * 255.0
                elif c == 2:
                    a = <float>img[y, x, 1] * 255.0
                else:
                    a = 255.0

                if c == 1 or c == 2: # Grayscale or LA
                    r = g = b = <float>img[y, x, 0] * 255.0
                else: # RGB or RGBA
                    r = <float>img[y, x, 0] * 255.0
                    g = <float>img[y, x, 1] * 255.0
                    b = <float>img[y, x, 2] * 255.0

                out[y, x, 0] = <unsigned char>(r if r < 255 else 255) if r > 0 else 0
                if target_c >= 3:
                    out[y, x, 1] = <unsigned char>(g if g < 255 else 255) if g > 0 else 0
                    out[y, x, 2] = <unsigned char>(b if b < 255 else 255) if b > 0 else 0
                if target_c == 4:
                    out[y, x, 3] = <unsigned char>(a if a < 255 else 255) if a > 0 else 0

    return np.asarray(out), target_c
