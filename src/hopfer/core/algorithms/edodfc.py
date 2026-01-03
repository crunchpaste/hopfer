import numpy as np
import logging

from .static import levien, nakano

logger = logging.getLogger(__name__)


def edodf(img, algorithm, settings):
    str = np.float64(settings["diffusion_factor"])
    hysteresis_c = np.float64(settings["hysteresis"])
    serpentine = settings["serpentine"]
    noise = settings["noise"]
    if noise:
        rng = np.random.default_rng()
        noise_array = rng.integers(low=0, high=32768, size=(20, img.shape[1])).astype(
            np.uint16
        )

        img = np.vstack((noise_array, img))

    if algorithm == "Levien":
        output_img = levien(img, str, hysteresis_c, serpentine)
    elif algorithm == "Nakano":
        logger.debug(f"Nakano : {algorithm}, {str}, {hysteresis_c}, {serpentine}")
        output_img = nakano(img, str, hysteresis_c, serpentine)
    else:
        # Default to Zhou-Fang serpentine
        output_img = levien(img, str, hysteresis_c, serpentine)

    if noise:
        output_img = output_img[20:, :]

    return output_img
