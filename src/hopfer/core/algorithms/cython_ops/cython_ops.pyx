# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True
# cython: nonecheck=False

import numpy as np
cimport numpy as cnp
from libc.stdint cimport uint8_t, uint16_t, uint32_t
from libcpp cimport bool
from cython.parallel import prange

ctypedef fused pixel_t:
    uint8_t
    uint16_t

ctypedef fused out_t:
    uint8_t
    uint16_t

# Grayscales
include "value.pxi"
include "lightness.pxi"
include "average.pxi"
include "luma.pxi"
include "luminance.pxi"
include "manual.pxi"

# Image adjustments
include "normalize.pxi"
include "equalize.pxi"
include "blur_caster.pxi"

# Halftoning

# Thresholds
include "sierra24a.pxi"
include "thresh.pxi"
include "niblack.pxi"
include "sauvola.pxi"
include "phansalkar.pxi"

# Random dithers
include "compare.pxi" # masks are generated in their respective modules e.g. mezzoc.py

# Ordered
include "ordered_dither.pxi"
include "ordered_dither_p.pxi"
# TODO: Add the perturbed one for Bayer

# Error Diffusion
include "ed.pxi" # raster scan
include "eds.pxi" # serpentine scan

# VED
include "ostromoukhov.pxi"
include "ostromoukhov_s.pxi"
include "zhou_fang_fast.pxi"
include "zhou_fang_fast_s.pxi"

# EDODF
include "nakano.pxi"
include "levien.pxi"

# Image styling
include "style_image.pxi"
include "style_alpha.pxi"

# Noise
include "noise_gen.pxi"
