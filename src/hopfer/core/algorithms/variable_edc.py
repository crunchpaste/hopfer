import numpy as np

from .static import ostromoukhov, ostromoukhov_s, zhou_fang, zhou_fang_s
from .ved_data import OSTROMOUKHOV_COEFFN, ZF_COEFFN, ZF_PERT


def variable_ed(img, algorithm, settings):
    str = settings["diffusion_factor"] / 100
    serpentine = settings["serpentine"]
    noise = settings["noise"]
    if noise:
        noise_array = np.random.random((20, img.shape[1])).astype(np.float32)
        img = np.vstack((noise_array, img))

    if algorithm == "Ostromoukhov":
        if serpentine:
            output_img = ostromoukhov_s(img, OSTROMOUKHOV_COEFFN, str)
        else:
            output_img = ostromoukhov(img, OSTROMOUKHOV_COEFFN, str)
    if algorithm == "Zhou-Fang":
        if serpentine:
            output_img = zhou_fang_s(img, ZF_COEFFN, ZF_PERT, str)
        else:
            output_img = zhou_fang(img, ZF_COEFFN, ZF_PERT, str)
    else:
        # Default to Zhou-Fang serpentine
        output_img = zhou_fang_s(img, ZF_COEFFN, ZF_PERT, str)

    if noise:
        output_img = output_img[20:, :]

    return output_img
