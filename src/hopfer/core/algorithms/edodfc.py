import numpy as np

from .static import levien, levien_s


def edodf(img, algorithm, settings):
    str = settings["diffusion_factor"] / 100
    hysteresis_c = settings["hysteresis"] / 100
    serpentine = settings["serpentine"]
    noise = settings["noise"]
    if noise:
        noise_array = np.random.random((20, img.shape[1])).astype(np.float32)
        img = np.vstack((noise_array, img))

    if algorithm == "Levien":
        if serpentine:
            output_img = levien_s(img, hysteresis_c, str)
        else:
            output_img = levien(img, hysteresis_c, str)
    else:
        # Default to Zhou-Fang serpentine
        output_img = levien(img, hysteresis_c, str)

    if noise:
        output_img = output_img[20:, :]

    return output_img
