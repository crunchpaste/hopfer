import numpy as np

from hopfer.core.algorithms.cython_ops import ed, eds, noise_gen, sierra24a


def error_diffusion(img, kernel, settings, algorithm):
    """
    Generic error diffusion function

    Args:
        img (np.ndarray): A 2d numpy array with the grayscale image.
        kernel (np.ndarray): A 2d numpy array with the error diffusion weights.
        settings (dict): Dictionary with the settings.
    Returns:
        output_img (np.ndarray): The dithered image as a 2d numpy array.
    """
    str = settings["diffusion_factor"]
    serpentine = settings["serpentine"]
    noise = settings["noise"]
    if noise:
        noise_array = noise_gen(np.uint16(img.shape[1]))
        img = np.vstack((noise_array, img))

    if algorithm != "Sierra2 4A":
        # a temporary solution until the rest of the ED's get hardcoded
        # currently only Sierra2 4A is hardcoded as it has a very small kernel and i had a lot of fun doing it.
        if serpentine:
            output_img = eds(img, kernel, str)
        else:
            output_img = ed(img, kernel, str)
    else:
        output_img = sierra24a(img, str, serpentine)

    if noise:
        output_img = output_img[20:, :]

    return output_img
