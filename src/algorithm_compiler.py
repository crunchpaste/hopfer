import numpy as np
from numba import prange
from numba.pycc import CC

# Initialize the compiler
cc = CC("static")
cc.output_dir = "src/algorithms"


# STYLING: Could later be used for outputting in different colors
@cc.export("style_image", "u1[:,:,:](f8[:,:], u1[:], u1[:])")
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
@cc.export("thresh", "f8[:,:](f8[:,:], f8)")
def thresh(img, threshold_value):
    # Apply thresholding
    h, w = img.shape
    output_img = np.zeros((h, w), dtype=np.float64)
    for i in range(h):
        for j in range(w):
            if img[i, j] > threshold_value:
                output_img[i, j] = 1.0
            else:
                output_img[i, j] = 0.0
    return output_img


@cc.export("niblack", "f8[:,:](f8[:,:], u2, f8)")
def niblack(img, n=25, k=0.2):
    # exaclty the same as sauvola() and phansalkar() apart for the formula for the threshold
    h, w = img.shape
    w_half = n // 2  # Half size of the block (window)

    output_img = np.zeros((h, w))

    # Compute the integral image and squared integral image
    integral_img = np.zeros((h + 1, w + 1))
    squared_integral_img = np.zeros((h + 1, w + 1))

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table

    for y in range(h):
        for x in range(w):
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]  # Left
                + integral_img[y, x + 1]  # Top
                - integral_img[y, x]  # Top left
                + img[y, x]  # Current
            )

            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]  # Left
                + squared_integral_img[y, x + 1]  # Top
                - squared_integral_img[y, x]  # Top left
                + img[y, x] ** 2  # Current
            )

    for y in range(h):
        # There seems to be no significant improvement in perfomance if doing it in a prange.
        for x in range(w):
            # Boundary checks
            y1, x1 = max(0, y - w_half), max(0, x - w_half)
            y2, x2 = min(h, y + w_half + 1), min(w, x + w_half + 1)

            # Get the sum of the block to calculate the mean
            block_sum = (
                integral_img[y2, x2]  # Bottom right
                - integral_img[y2, x1]  # Left
                - integral_img[y1, x2]  # Top
                + integral_img[y1, x1]  # Top left
            )

            block_sq_sum = (
                squared_integral_img[y2, x2]  # Bottom right
                - squared_integral_img[y2, x1]  # Left
                - squared_integral_img[y1, x2]  # Top
                + squared_integral_img[y1, x1]  # Top left
            )

            block_area = (y2 - y1) * (x2 - x1)

            mean = block_sum / block_area
            mean_sq = block_sq_sum / block_area
            variance = mean_sq - mean**2

            # if variance gets to be negative strange glitches start happening
            if variance <= 0:
                variance = 0

            std = np.sqrt(variance)

            # Get the threshold for the current pixel using the formula provided by craft of coding: https://craftofcoding.wordpress.com/2021/09/30/thresholding-algorithms-niblack-local/
            threshold = mean - k * std

            # Check against the calculated threshold
            if img[y, x] > threshold:
                output_img[y, x] = 1
            else:
                output_img[y, x] = 0

    return output_img


@cc.export("sauvola", "f8[:,:](f8[:,:], u2, f8, f8)")
def sauvola(img, n=25, R=0.5, k=0.2):
    h, w = img.shape
    w_half = n // 2  # Half size of the block (window)

    output_img = np.zeros((h, w))

    # Compute the integral image and squared integral image
    integral_img = np.zeros((h + 1, w + 1))
    squared_integral_img = np.zeros((h + 1, w + 1))

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table. This could probably be done just once and be stored in the ImageStorage class...

    for y in range(h):
        for x in range(w):
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]  # Left
                + integral_img[y, x + 1]  # Top
                - integral_img[y, x]  # Top left
                + img[y, x]  # Current
            )

            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]  # Left
                + squared_integral_img[y, x + 1]  # Top
                - squared_integral_img[y, x]  # Top left
                + img[y, x] ** 2  # Current
            )

    for y in range(h):
        # There seems to be no significant improvement in perfomance if doing it in a prange.
        for x in range(w):
            # Boundary checks
            y1, x1 = max(0, y - w_half), max(0, x - w_half)
            y2, x2 = min(h, y + w_half + 1), min(w, x + w_half + 1)

            # Get the sum of the block to calculate the mean
            block_sum = (
                integral_img[y2, x2]  # Bottom right
                - integral_img[y2, x1]  # Left
                - integral_img[y1, x2]  # Top
                + integral_img[y1, x1]  # Top left
            )

            block_sq_sum = (
                squared_integral_img[y2, x2]  # Bottom right
                - squared_integral_img[y2, x1]  # Left
                - squared_integral_img[y1, x2]  # Top
                + squared_integral_img[y1, x1]  # Top left
            )

            block_area = (y2 - y1) * (x2 - x1)

            mean = block_sum / block_area
            mean_sq = block_sq_sum / block_area
            variance = mean_sq - mean**2

            # if variance gets to be negative strange glitches start happening
            if variance <= 0:
                variance = 0

            std = np.sqrt(variance)

            # Get the threshold for the current pixel using the formula provided by craft of coding: https://craftofcoding.wordpress.com/2021/10/06/thresholding-algorithms-sauvola-local/
            threshold = mean * (1 + k * ((std / R) - 1))

            # Check against the calculated threshold
            if img[y, x] > threshold:
                output_img[y, x] = 1
            else:
                output_img[y, x] = 0

    return output_img


@cc.export("phansalkar", "f8[:,:](f8[:,:], u2, f8, f8, f8, f8)")
def phansalkar(img, n=25, R=0.5, k=0.2, p=3, q=10):
    # This function is completely duplicating seuvola, apart from the arguments accepted and the formula for the local threshold. This is mostly done to for marginal performance gains by avoiding some conditionals.
    h, w = img.shape
    w_half = n // 2  # Half size of the block (window)

    output_img = np.zeros((h, w))

    # Compute the integral image and squared integral image
    integral_img = np.zeros((h + 1, w + 1))
    squared_integral_img = np.zeros((h + 1, w + 1))

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table. This could probably be done just once and be stored in the ImageStorage class...

    for y in range(h):
        for x in range(w):
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]  # Left
                + integral_img[y, x + 1]  # Top
                - integral_img[y, x]  # Top left
                + img[y, x]  # Current
            )

            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]  # Left
                + squared_integral_img[y, x + 1]  # Top
                - squared_integral_img[y, x]  # Top left
                + img[y, x] ** 2  # Current
            )

    for y in range(h):
        # There seems to be no significant improvement in perfomance if doing it in a prange.
        for x in range(w):
            # Boundary checks
            y1, x1 = max(0, y - w_half), max(0, x - w_half)
            y2, x2 = min(h, y + w_half + 1), min(w, x + w_half + 1)

            # Get the sum of the block to calculate the mean
            block_sum = (
                integral_img[y2, x2]  # Bottom right
                - integral_img[y2, x1]  # Left
                - integral_img[y1, x2]  # Top
                + integral_img[y1, x1]  # Top left
            )

            block_sq_sum = (
                squared_integral_img[y2, x2]  # Bottom right
                - squared_integral_img[y2, x1]  # Left
                - squared_integral_img[y1, x2]  # Top
                + squared_integral_img[y1, x1]  # Top left
            )

            block_area = (y2 - y1) * (x2 - x1)

            mean = block_sum / block_area
            mean_sq = block_sq_sum / block_area
            variance = mean_sq - mean**2

            # if variance gets to be negative strange glitches start happening
            if variance <= 0:
                variance = 0

            std = np.sqrt(variance)

            # Get the threshold for the current pixel using the formula provided by craft of coding: https://craftofcoding.wordpress.com/2021/09/28/thresholding-algorithms-phansalkar-local/
            threshold = mean * (1 + p * np.exp(-q * mean) + k * ((std / R) - 1))

            # Check against the calculated threshold
            if img[y, x] > threshold:
                output_img[y, x] = 1
            else:
                output_img[y, x] = 0

    return output_img


# NOISE RELATED FUNCTIONS


@cc.export("compare", "f8[:,:](f8[:,:], f8[:,:], u2, u2)")
def compare(img, noise, h, w):
    # Doing it in this crude nested for loop seems to be a few times faster than using np.where
    for y in range(h):
        for x in range(w):
            if noise[y, x] > img[y, x]:
                img[y, x] = 0
            else:
                img[y, x] = 1
    return img


@cc.export("bayer_dither", "f8[:,:](f8[:,:], f8[:,:])")
def bayer_dither(img, matrix):
    n = matrix.shape[0]
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            pixel = img[y, x]
            j = y % n
            if not (pixel == 0 or pixel == 1):
                i = x % n
                if matrix[j, i] > img[y, x]:
                    img[y, x] = 0
                else:
                    img[y, x] = 1

    return img


# ERROR DIFFUSION FUNCTIONS. At some point EDOFDs should be added
@cc.export("ed", "f8[:,:](f8[:,:], f8[:,:], f8)")
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


# Same as above SERPENTINE
@cc.export("eds", "f8[:,:](f8[:,:], f8[:,:], f8)")
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
        img = np.fliplr(img)

    return img  # return the image in a dithered form


# GRAYSCALE CONVERSION functions follow.
@cc.export("luminance", "f8[:,:](f8[:,:,:])")
def luminance(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w), dtype=np.float64)

    for y in range(h):
        for x in range(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = 0.22 * r + 0.72 * g + 0.06 * b
    return output_img


@cc.export("luma", "f8[:,:](f8[:,:,:])")
def luma(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = 0.30 * r + 0.59 * g + 0.11 * b

    return output_img


@cc.export("average", "f8[:,:](f8[:,:,:])")
def average(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            r, g, b = img[y, x, 0:3]
            output_img[y, x] = (r + g + b) / 3

    return output_img


@cc.export("value", "f8[:,:](f8[:,:,:])")
def value(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            values = img[y, x, 0:3]
            output_img[y, x] = np.max(values)

    return output_img


@cc.export("lightness", "f8[:,:](f8[:,:,:])")
def lightness(img):
    h, w, _ = img.shape
    output_img = np.zeros((h, w))

    for y in prange(h):
        for x in prange(w):
            values = img[y, x, 0:3]
            max = np.max(values)
            min = np.min(values)
            output_img[y, x] = (max + min) * 0.5

    return output_img


# The IMAGE PROCESSING fuctions should go here if i decide to implement them from scratch instead of using pillow
@cc.export("sharpen", "f8[:,:](f8[:,:],f8)")
def sharpen(image, str=1.0):
    str *= 0.1
    x = str + 1.0
    y = -str / 4

    # A classic sharpening kernel found on wiki
    kernel = np.array([[0, y, 0], [y, x, y], [0, y, 0]]).astype(np.float32)

    # Create a padded image to avoid out of bounds error
    padded_image = np.zeros((image.shape[0] + 2, image.shape[1] + 2)).astype(np.float32)
    padded_image[1:-1, 1:-1] = image

    sharpened = np.zeros((image.shape[0], image.shape[1]))

    for i in prange(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded_image[i : i + 3, j : j + 3]  # Extract the 3x3 region
            sharpened[i, j] = np.sum(region * kernel)  # Apply the kernel

    return sharpened


if __name__ == "__main__":
    cc.compile()
