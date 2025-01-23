from numba import prange
from numba.pycc import CC
import numpy as np

# Initialize the compiler
cc = CC('static')
cc.output_dir = "src/algorithms"

@cc.export('thresh', 'f8[:,:](f8[:,:], f8)')
def thresh(img, threshold_value):
    # Apply thresholding
    output_img = img.copy()
    h,w = img.shape
    # output = image.flatten()
    for i in range(h):
        for j in range(w):
            if output_img[i, j] > threshold_value:
                output_img[i, j] = 1
            else:
                output_img[i, j] = 0
    # thresholded_image = np.where(image >= threshold_value, 1, 0)

    return output_img
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

@cc.export('luminance', 'f8[:,:](f8[:,:,:])')
def luminance(img):

    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = (0.22 * r + 0.72 * g + 0.06 * b)

    return output_img

@cc.export('luma', 'f8[:,:](f8[:,:,:])')
def luma(img):

    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = (0.30 * r + 0.59 * g + 0.11 * b)

    return output_img

@cc.export('average', 'f8[:,:](f8[:,:,:])')
def average(img):

    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = (r + g + b) / 3

    return output_img

@cc.export('value', 'f8[:,:](f8[:,:,:])')
def value(img):

    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            values = img[y, x, 0:3]
            output_img[y, x] = np.max(values)

    return output_img

@cc.export('lightness', 'f8[:,:](f8[:,:,:])')
def lightness(img):

    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            values = img[y, x, 0:3]
            max = np.max(values)
            min = np.min(values)
            output_img[y, x] = (max + min) * .5

    return output_img

# Compile the code and create the shared library (.so file)
if __name__ == "__main__":
    cc.compile()

@cc.export('sharpen', 'f8[:,:](f8[:,:],f8)')
def sharpen(image, str=1.0):
    str *= 0.1
    x = str + 1.0
    y = -str / 4

    # A classic sharpening kernel found on wiki
    kernel = np.array([
        [0, y, 0],
        [y, x, y],
        [0, y, 0]
    ]).astype(np.float32)

    # Create a padded image to avoid out of bounds error
    padded_image = np.zeros((image.shape[0] + 2, image.shape[1] + 2)).astype(np.float32)
    padded_image[1:-1, 1:-1] = image

    sharpened = np.zeros((image.shape[0], image.shape[1]))

    for i in prange(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded_image[i:i+3, j:j+3]  # Extract the 3x3 region
            sharpened[i, j] = np.sum(region * kernel)  # Apply the kernel

    return sharpened

# Compile the code and create the shared library (.so file)
if __name__ == "__main__":
    cc.compile()
