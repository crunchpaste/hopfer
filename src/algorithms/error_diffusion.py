import numpy as np
from numba import njit


def error_diffusion(img, kernel, settings):
    """
    Generic error diffusion function.

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


@njit(cache=True)
def ed(img, kernel, str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused.
    """

    height, width = img.shape

    # iterating over aranges seems much faster than the python range() for big arrays. tried using ndenumerate but it was slower and flatiter but it isn't fully supported.
    h, w = np.arange(height), np.arange(width)

    kernel_height, kernel_width = kernel.shape[0], kernel.shape[1]

    kernel_center_x, kernel_center_y = kernel_width // 2, kernel_height // 2

    for y in h:
        for x in w:
            old_pixel = img[y, x]
            # np.rint() is marginally faster that np.round() which itself was much faster than a conditional. as precision was not needed, rint() is used.
            new_pixel = np.rint(old_pixel)

            img[y, x] = new_pixel  # replace the value in place
            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if (
                        kernel[ky, kx] != 0
                        # check if there is something at the index to diffuse. this led to the biggest improvement in speed.
                        and 0 <= y + ky - kernel_center_y < height
                        and 0 <= x + kx - kernel_center_x < width
                    ):  # check if the pixel is even inside the image. I've tried padding the image to avoid this check but it didn't seem to matter at all.
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += (
                            error * kernel[ky, kx]
                        )
                        # actually diffuse the error maybe the index could be precomputed

    return img  # return the image in a dithered form


@njit(cache=True)
def eds(img, kernel, str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused. This is the serpentine version. It was separated for performance reasons.
    """

    height, width = img.shape

    # iterating over aranges seems much faster than the python range() for big arrays. tried using ndenumerate but it was slower and flatiter but it isn't fully supported.
    h, w = np.arange(height), np.arange(width)

    kernel_height, kernel_width = kernel.shape[0], kernel.shape[1]

    kernel_center_x, kernel_center_y = kernel_width // 2, kernel_height // 2

    for y in h:
        img = np.fliplr(
            img
        )  # flipping the whole image seems like an easy way to do a serpentine raster.
        for x in w:
            old_pixel = img[y, x]
            # np.rint() is marginally faster that np.round() which itself was much faster than a conditional. as precision was not needed, rint() is used.
            new_pixel = np.rint(old_pixel)

            img[y, x] = new_pixel  # replace the value in place
            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if (
                        kernel[ky, kx] != 0
                        # check if there is something at the index to diffuse. this led to the biggest improvement in speed.
                        and 0 <= y + ky - kernel_center_y < height
                        and 0 <= x + kx - kernel_center_x < width
                    ):  # check if the pixel is even inside the image. I've tried padding the image to avoid this check but it didn't seem to matter at all.
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += (
                            error * kernel[ky, kx]
                        )
                        # actually diffuse the error maybe the index could be precomputed
    if h.size % 2 != 0:
        img = np.fliplr(img)

    return img  # return the image in a dithered form
