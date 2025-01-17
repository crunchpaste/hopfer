import numpy as np
from numba import njit

def error_diffusion(img, kernel, settings):
    str = settings['diffusion_factor'] / 100
    serpentine = settings['serpentine']
    print(str, serpentine)
    if serpentine:
        output_img = eds(img, kernel, str)
    else:
        output_img = ed(img, kernel, str)

    return output_img

@njit(cache=True)
def ed(img, kernel, str):
    height, width = img.shape
    output_img = np.zeros_like(img)

    kernel_height, kernel_width = kernel.shape
    kernel_center_x, kernel_center_y = kernel_width // 2, kernel_height // 2

    for y in range(height):
        for x in range(width):
            old_pixel = img[y, x]

            if old_pixel >= 0.5:
                new_pixel = 1
            else:
                new_pixel = 0

            output_img[y, x] = new_pixel
            error = (old_pixel - new_pixel) * str

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if (0 <= y + ky - kernel_center_y < height and
                        0 <= x + kx - kernel_center_x < width):
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += error * kernel[ky, kx]

    return output_img

@njit(cache=True)
def eds(img, kernel, str):
    height, width = img.shape
    output_img = np.zeros_like(img)

    kernel_height, kernel_width = kernel.shape
    kernel_center_x, kernel_center_y = kernel_width // 2, kernel_height // 2

    flipped = False

    for y in range(height):
        if y % 2 == 0:
            flipped = True
        else:
            flipped = False

        img = np.fliplr(img)
        # kernel = np.fliplr(kernel)
        output_img = np.fliplr(output_img)

        for x in range(width):
            old_pixel = img[y, x]

            if old_pixel >= 0.5:
                new_pixel = 1
            else:
                new_pixel = 0

            output_img[y, x] = new_pixel
            error = (old_pixel - new_pixel) * str

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if 0 <= y + ky - kernel_center_y < height and 0 <= x + kx - kernel_center_x < width:
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += error * kernel[ky, kx]

    if flipped:
        output_img = np.fliplr(output_img)

    return output_img
