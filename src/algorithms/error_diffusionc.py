from .static import ed, eds


def error_diffusion(img, kernel, settings):
    """
    Generic error diffusion function

    Args:
        img (np.ndarray): A 2d numpy array with the grayscale image.
        kernel (np.ndarray): A 2d numpy array with the error diffusion weights.
        settings (dict): Dictionary with the settings.
    Returns:
        output_img (np.ndarray): The dithered image as a 2d numpy array.
    """
    str = settings["diffusion_factor"] / 100
    serpentine = settings["serpentine"]
    print(str, serpentine)
    if serpentine:
        output_img = eds(img, kernel, str)
    else:
        output_img = ed(img, kernel, str)

    return output_img
