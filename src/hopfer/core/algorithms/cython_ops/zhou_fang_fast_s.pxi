# zhou_fang_s.pxi
from libc.stdint cimport int32_t, uint8_t, uint16_t, uint32_t, uint64_t

def zhou_fang_fast_s(img_u16, coeff_array, pert_array, double str_value):
    cdef int h = img_u16.shape[0]
    cdef int w = img_u16.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef int32_t[:, :] img = np.array(img_u16, dtype=np.int32)
    cdef double[:] pert_buf = np.array(pert_array, dtype=np.float64)
    cdef double[:] c0_table = np.array(coeff_array[:, 0], dtype=np.float64)
    cdef double[:] c1_table = np.array(coeff_array[:, 1], dtype=np.float64)
    cdef double[:] c2_table = np.array(coeff_array[:, 2], dtype=np.float64)
    _zhou_fang_s_core(img, pert_buf, c0_table, c1_table, c2_table, out, h, w, str_value)
    return out.view(np.bool_)

cdef void _zhou_fang_s_core(
    int32_t[:, :] img,
    double[:] pert_array,
    double[:] c0_table,
    double[:] c1_table,
    double[:] c2_table,
    uint8_t[:, :] out,
    int h, int w,
    double str_value
) noexcept nogil:
    cdef int y, x, coeff_idx
    cdef int32_t old_value, new_value, e_int, pert_mod
    cdef int32_t THRESHOLD = 32768
    cdef uint64_t mcg_state = <uint64_t>0xCAFEF00DD15EA5E5
    cdef uint64_t MULT = <uint64_t>6364136223846793005
    cdef uint64_t x_bits
    cdef uint32_t count, rng_val_u32, pert
    cdef double c0, c1, c2, error
    cdef bint reverse

    for y in range(h):
        reverse = (y & 1) == 0
        for x in range(w):
            # Generate a random float using pcg32_fast (https://en.wikipedia.org/wiki/Permuted_congruential_generator)
            # This seems to be almost twice as fast as numpy's random module and produces noise that to me looks just as nice.
            x_bits = mcg_state
            count = <uint32_t>(x_bits >> 61)
            # advance
            mcg_state = x_bits * MULT
            x_bits ^= x_bits >> 22
            rng_val_u32 = <uint32_t>(x_bits >> (22 + count))
            # getting the random number as a float seems to be just as fast, then again i think its cleaner to just get the in the range we already nee it.
            # rand_float = <double>rng_val_u32 * 2.3283064365386963e-10
            pert = rng_val_u32 >> 17
            # map logical x to actual column depending on scan direction
            x = x if not reverse else (w - 1 - x)
            old_value = img[y, x]
            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255
            pert_mod = <int32_t>(pert * pert_array[coeff_idx])
            if (old_value + pert_mod) >= THRESHOLD:
                new_value = 65535
                out[y, x] = 1
            else:
                new_value = 0
                out[y, x] = 0
            error = (old_value - new_value) * str_value
            e_int = <int32_t>error
            c0 = c0_table[coeff_idx]
            c1 = c1_table[coeff_idx]
            c2 = c2_table[coeff_idx]
            if not reverse:
                if x + 1 < w:
                    img[y, x + 1] += <int32_t>(e_int * c0)
                if x - 1 >= 0 and y + 1 < h:
                    img[y + 1, x - 1] += <int32_t>(e_int * c1)
            else:
                if x - 1 >= 0:
                    img[y, x - 1] += <int32_t>(e_int * c0)
                if x + 1 < w and y + 1 < h:
                    img[y + 1, x + 1] += <int32_t>(e_int * c1)
            # Vertical always uses c2
            if y + 1 < h:
                img[y + 1, x] += <int32_t>(e_int * c2)
