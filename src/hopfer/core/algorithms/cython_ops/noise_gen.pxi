# noise_gen.pxi
from libc.stdint cimport uint16_t, uint32_t, uint64_t

def noise_gen(uint16_t w):
    cdef int h = 20
    out = np.zeros((h, w), dtype=np.uint16)
    cdef uint16_t[:, :] noise = out
    _noise_gen_core(noise, h, w)
    return out

cdef void _noise_gen_core(uint16_t[:, :] noise, int h, int w) noexcept nogil:
    cdef int y, x
    cdef uint64_t mcg_state = <uint64_t>0xCAFEF00DD15EA5E5
    cdef uint64_t MULT = <uint64_t>6364136223846793005
    cdef uint64_t x_bits
    cdef uint32_t count, rng_val_u32

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
            noise[y, x] = <uint16_t>(rng_val_u32 >> 16)
