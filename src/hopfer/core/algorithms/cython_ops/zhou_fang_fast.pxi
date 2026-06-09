# zhou_fang.pxi
from libc.stdint cimport int16_t, int32_t, uint8_t, uint16_t, uint32_t, uint64_t

def zhou_fang_fast(img_u16, coeff_array, pert_array, double str_value):
    cdef int h = img_u16.shape[0]
    cdef int w = img_u16.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef int16_t[:, :] img = (img_u16 >> 2).astype(np.int16)
    cdef double[:, :] coeff_buf = np.array(coeff_array, dtype=np.float64)
    cdef double[:] pert_buf = np.array(pert_array, dtype=np.float64)
    # Pre-compute coefficient tables
    cdef double[:] c0_table = np.array(coeff_array[:, 0] * str_value, dtype=np.float64)
    cdef double[:] c1_table = np.array(coeff_array[:, 1] * str_value, dtype=np.float64)
    cdef double[:] c2_table = np.array(coeff_array[:, 2] * str_value, dtype=np.float64)
    _zhou_fang_core(img, pert_buf, c0_table, c1_table, c2_table, out, h, w)
    return out.view(np.bool_)

cdef void _zhou_fang_core(
    int16_t[:, :] img,
    double[:] pert_array,
    double[:] c0_table,
    double[:] c1_table,
    double[:] c2_table,
    uint8_t[:, :] out,
    int h, int w
) noexcept nogil:
    cdef int y, x, coeff_idx
    cdef int16_t old_value, new_value
    cdef int32_t error, pert_mod
    cdef int32_t THRESHOLD = 8192
    cdef uint64_t mcg_state = <uint64_t>0xCAFEF00DD15EA5E5
    cdef uint64_t MULT = <uint64_t>6364136223846793005
    cdef uint64_t x_bits
    cdef uint32_t count, rng_val_u32, pert
    cdef double c0, c1, c2

    for y in range(h):
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
            old_value = img[y, x]
            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255
            pert_mod = <int32_t>(pert * pert_array[coeff_idx])
            if (old_value + pert_mod) >= THRESHOLD:
                new_value = 16383
                out[y, x] = 1
            else:
                new_value = 0
                out[y, x] = 0
            error = <int32_t>(old_value - new_value)
            c0 = c0_table[coeff_idx]
            c1 = c1_table[coeff_idx]
            c2 = c2_table[coeff_idx]
            if x + 1 < w:
                img[y, x + 1] += <int16_t>(error * c0)
            if x - 1 >= 0 and y + 1 < h:
                img[y + 1, x - 1] += <int16_t>(error * c1)
            if y + 1 < h:
                img[y + 1, x] += <int16_t>(error * c2)
