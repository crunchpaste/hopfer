from numba.pycc import CC
import numpy as np

# Initialize the compiler
cc = CC('static')
cc.output_dir = "src/algorithms/compiled"

# Export the function with the appropriate signature (for example, using f8 for float64)
@cc.export('ed', 'f8[:,:](f8[:,:], f8[:,:], f8)')
def ed(img, kernel, str_value):
    """
    Applies a dithering algorithm using a kernel to an image.
    """
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
            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if (0 <= y + ky - kernel_center_y < height and
                        0 <= x + kx - kernel_center_x < width):
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += error * kernel[ky, kx]

    return output_img

# Export the second function `eds`
@cc.export('eds', 'f8[:,:](f8[:,:], f8[:,:], f8)')
def eds(img, kernel, str_value):
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
            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if 0 <= y + ky - kernel_center_y < height and 0 <= x + kx - kernel_center_x < width:
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += error * kernel[ky, kx]

    if flipped:
        output_img = np.fliplr(output_img)

    return output_img

# Compile the code and create the shared library (.so file)
if __name__ == "__main__":
    cc.compile()
