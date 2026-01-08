# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

import numpy as np
cimport numpy as cnp
from libc.stdint cimport uint8_t, uint16_t, uint32_t
from libcpp cimport bool
from cython.parallel import prange

ctypedef fused pixel_t:
    uint8_t
    uint16_t

# Define another for the output so they can be different
ctypedef fused out_t:
    uint8_t
    uint16_t

include "value.pxi"
include "lightness.pxi"
include "average.pxi"
include "luma.pxi"
include "luminance.pxi"
include "manual.pxi"
