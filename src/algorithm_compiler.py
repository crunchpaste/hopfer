from numba import prange
from numba.pycc import CC
import numpy as np

# Initialize the compiler
cc = CC('static')
cc.output_dir = "src/algorithms"


# STYLING: Could later be used for outputting in different colors
@cc.export('style_image', 'u1[:,:,:](f8[:,:], u1[:], u1[:])')
def style_image(img, black, white):
    h, w = img.shape
    output_img = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            if img[y, x] == 0:
                output_img[y, x, 0] = black[0]
                output_img[y, x, 1] = black[1]
                output_img[y, x, 2] = black[2]
            else:
                output_img[y, x, 0] = white[0]
                output_img[y, x, 1] = white[1]
                output_img[y, x, 2] = white[2]
    return output_img

# THESHOLDING METHODS. Should include local thresholding later.
@cc.export('thresh', 'f8[:,:](f8[:,:], f8)')
def thresh(img, threshold_value):
    # Apply thresholding
    h,w = img.shape
    output_img = np.zeros((h,w), dtype=np.float64)
    for i in range(h):
        for j in range(w):
            if img[i, j] > threshold_value:
                output_img[i, j] = 1.0
            else:
                output_img[i, j] = 0.0
    return output_img

# ERROR DIFFUSION FUNCTIONS. At some point EDOFDs should be added
@cc.export('ed', 'f8[:,:](f8[:,:], f8[:,:], f8)')
def ed(img, kernel, str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused.
    """

    height, width = img.shape

    # iterating over aranges seems much faster than the python range() for big arrays. tried using ndenumerate but it was slower and flatiter but it isn't fully supported.
    h, w = np.arange(height), \
           np.arange(width)

    kernel_height, kernel_width = kernel.shape[0],\
                                  kernel.shape[1]

    kernel_center_x, kernel_center_y = kernel_width // 2, \
                                       kernel_height // 2

    for y in h:
        for x in w:
            old_pixel = img[y, x]
            # np.rint() is marginally faster that np.round() which itself was much faster than a conditional. as precision was not needed, rint() is used.
            new_pixel = np.rint(old_pixel)

            img[y, x] = new_pixel # replace the value in place
            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if kernel[ky,kx] != 0: # check if there is something at the index to diffuse. this led to the biggest improvement in speed.
                        if (0 <= y + ky - kernel_center_y < height and
                            0 <= x + kx - kernel_center_x < width): # check if the pixel is even inside the image. I've tried padding the image to avoid this check but it didn't seem to matter at all.

                            img[y + ky - kernel_center_y,
                                x + kx - kernel_center_x] += error * kernel[ky, kx] # actually diffuse the error maybe the index could be precomputed

    return img # return the image in a dithered form

# Same as above SERPENTINE
@cc.export('eds', 'f8[:,:](f8[:,:], f8[:,:], f8)')
def eds(img, kernel, str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused. This is the serpentine version. It was separated for performance reasons.
    """

    height, width = img.shape

    # iterating over aranges seems much faster than the python range() for big arrays. tried using ndenumerate but it was slower and flatiter but it isn't fully supported.
    h, w = np.arange(height), \
           np.arange(width)

    kernel_height, kernel_width = kernel.shape[0],\
                                  kernel.shape[1]

    kernel_center_x, kernel_center_y = kernel_width // 2, \
                                       kernel_height // 2

    for y in h:
        img = np.fliplr(img) # flipping the whole image seems like an easy way to do a serpentine raster.
        for x in w:
            old_pixel = img[y, x]
            # np.rint() is marginally faster that np.round() which itself was much faster than a conditional. as precision was not needed, rint() is used.
            new_pixel = np.rint(old_pixel)

            img[y, x] = new_pixel # replace the value in place
            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if kernel[ky,kx] != 0: # check if there is something at the index to diffuse. this led to the biggest improvement in speed.
                        if (0 <= y + ky - kernel_center_y < height and
                            0 <= x + kx - kernel_center_x < width): # check if the pixel is even inside the image. I've tried padding the image to avoid this check but it didn't seem to matter at all.

                            img[y + ky - kernel_center_y,
                                x + kx - kernel_center_x] += error * kernel[ky, kx] # actually diffuse the error maybe the index could be precomputed
    if h.size % 2 != 0:
        img = np.fliplr(img)

    return img # return the image in a dithered form

# GRAYSCALE CONVERSION functions follow.
@cc.export('luminance', 'f8[:,:](f8[:,:,:])')
def luminance(img):

    h, w, _ = img.shape
    output_img = np.zeros((h, w), dtype=np.float64)

    for y in range(h):
        for x in range(w):
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

# The IMAGE PROCESSING fuctions should go here if i decide to implement them from scratch instead of using pillow
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

if __name__ == "__main__":
    cc.compile()
