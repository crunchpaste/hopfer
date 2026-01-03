import os
from pathlib import Path

import numpy as np
from numba import uint8
from numba.pycc import CC

BASE_DIR = Path(__file__).resolve().parent.parent / "algorithms"

# Initialize the compiler
cc = CC("static")
cc.output_dir = os.fspath(BASE_DIR)


# STYLING: Could later be used for outputting in different colors
@cc.export("style_image", "u1[:,:,:](b1[:,:], u1[:], u1[:])")
def style_image(img, black, white):
    h, w = img.shape
    output_img = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            if img[y, x]:
                output_img[y, x, 0] = white[0]
                output_img[y, x, 1] = white[1]
                output_img[y, x, 2] = white[2]
            else:
                output_img[y, x, 0] = black[0]
                output_img[y, x, 1] = black[1]
                output_img[y, x, 2] = black[2]
    return output_img


# It seems to be much faster to just style and composite in one step
# instead of calling separate functions for it
@cc.export("style_alpha", "u1[:,:,:](u1[:,:], b1[:,:], u1[:], u1[:], u1[:])")
def style_alpha(img, alpha_img, black, white, alpha):
    h, w = img.shape
    output_img = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            a_val = alpha_img[y, x]
            a_inv = 255 - a_val

            if img[y, x]:
                c_r, c_g, c_b = black[0], black[1], black[2]
            else:
                c_r, c_g, c_b = white[0], white[1], white[2]

            output_img[y, x, 0] = uint8((c_r * a_val + alpha[0] * a_inv + 127) // 255)
            output_img[y, x, 1] = uint8((c_g * a_val + alpha[1] * a_inv + 127) // 255)
            output_img[y, x, 2] = uint8((c_b * a_val + alpha[2] * a_inv + 127) // 255)

    return output_img


# THESHOLDING METHODS.
@cc.export("thresh", "b1[:,:](u1[:,:], f4)")
def thresh(img, threshold_value):
    # Apply thresholding
    thresh_v = threshold_value * 255
    h, w = img.shape
    output_img = np.zeros((h, w), dtype=np.bool)
    for i in range(h):
        for j in range(w):
            if img[i, j] > thresh_v:
                output_img[i, j] = True
            else:
                output_img[i, j] = False
    return output_img


@cc.export("niblack", "b1[:,:](u1[:,:], u2, f4)")
def niblack(img, n=25, k=0.2):
    # exaclty the same as sauvola() and phansalkar() apart for the formula for the threshold
    h, w = img.shape
    w_half = n // 2  # Half size of the block (window)

    output_img = np.zeros((h, w), dtype=np.bool_)

    # Compute the integral image and squared integral image
    # We use float64 (f8) because the sums for a large image will overflow 32-bit types
    integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    squared_integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table

    for y in range(h):
        for x in range(w):
            val = np.float64(img[y, x])
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]  # Left
                + integral_img[y, x + 1]  # Top
                - integral_img[y, x]  # Top left
                + val  # Current
            )

            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]  # Left
                + squared_integral_img[y, x + 1]  # Top
                - squared_integral_img[y, x]  # Top left
                + val**2  # Current
            )

    for y in range(h):
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
                output_img[y, x] = True
            else:
                output_img[y, x] = False

    return output_img


@cc.export("sauvola", "b1[:,:](u1[:,:], u2, f8, f8)")
def sauvola(img, n=25, R=0.5, k=0.2):
    h, w = img.shape
    w_half = n // 2  # Half size of the block (window)

    # Scaling R internally to keep the UI the same
    R_scaled = R * 255.0 + 1

    output_img = np.zeros((h, w), dtype=np.bool_)

    # Compute the integral image and squared integral image
    integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    squared_integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table. This could probably be done just once and be stored in the ImageStorage class...

    for y in range(h):
        for x in range(w):
            val = np.float64(img[y, x])
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]  # Left
                + integral_img[y, x + 1]  # Top
                - integral_img[y, x]  # Top left
                + val  # Current
            )

            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]  # Left
                + squared_integral_img[y, x + 1]  # Top
                - squared_integral_img[y, x]  # Top left
                + val**2  # Current
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
            threshold = mean * (1 + k * ((std / R_scaled) - 1))

            # Check against the calculated threshold
            if img[y, x] > threshold:
                output_img[y, x] = True
            else:
                output_img[y, x] = False

    return output_img


@cc.export("phansalkar", "b1[:,:](u1[:,:], u2, f8, f8, f8, f8)")
def phansalkar(img, n=25, R=0.5, k=0.2, p=3.0, q=10.0):
    # This function is completely duplicating seuvola, apart from the arguments accepted and the formula for the local threshold. This is mostly done to for marginal performance gains by avoiding some conditionals.
    h, w = img.shape
    w_half = n // 2  # Half size of the block (window)

    # Scale R to match uint8 range (0-255)
    R_scaled = R * 255.0
    if R_scaled <= 0:
        R_scaled = 1.0

    output_img = np.zeros((h, w), dtype=np.bool_)

    # Compute the integral image and squared integral image
    # Using float64 is mandatory for 24MP images to prevent overflow
    integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    squared_integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table. This could probably be done just once and be stored in the ImageStorage class...

    for y in range(h):
        for x in range(w):
            val = np.float64(img[y, x])
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]  # Left
                + integral_img[y, x + 1]  # Top
                - integral_img[y, x]  # Top left
                + val  # Current
            )

            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]  # Left
                + squared_integral_img[y, x + 1]  # Top
                - squared_integral_img[y, x]  # Top left
                + (val * val)  # Current
            )

    for y in range(h):
        # There seems to be no significant improvement in perfomance if doing it in a prange.
        for x in range(w):
            # Boundary checks
            y1, x1 = max(0, y - w_half), max(0, x - w_half)
            y2, x2 = min(h, y + w_half + 1), min(w, x + w_half + 1)

            area = np.float64((y2 - y1) * (x2 - x1))

            # Get the sum of the block to calculate the mean
            s = (
                integral_img[y2, x2]  # Bottom right
                - integral_img[y2, x1]  # Left
                - integral_img[y1, x2]  # Top
                + integral_img[y1, x1]  # Top left
            )

            sq_s = (
                squared_integral_img[y2, x2]  # Bottom right
                - squared_integral_img[y2, x1]  # Left
                - squared_integral_img[y1, x2]  # Top
                + squared_integral_img[y1, x1]  # Top left
            )

            mean = s / area

            # Stable variance calculation
            variance = (sq_s - (s * s) / area) / area

            if variance <= 0:
                std = 0.0
            else:
                std = np.sqrt(variance)

            # Get the threshold for the current pixel using the formula provided by craft of coding: https://craftofcoding.wordpress.com/2021/09/28/thresholding-algorithms-phansalkar-local/
            # Mean is divided by 255 to keep the exponential term consistent with the original 0.0-1.0 logic.
            threshold = mean * (
                1.0 + p * np.exp(-q * (mean / 255.0)) + k * ((std / R_scaled) - 1.0)
            )

            # Check against the calculated threshold
            if np.float64(img[y, x]) > threshold:
                output_img[y, x] = True
            else:
                output_img[y, x] = False

    return output_img


# NOISE RELATED FUNCTIONS


@cc.export("compare", "b1[:,:](u1[:,:], u1[:,:], u2, u2)")
def compare(img, noise, h, w):
    # Doing it in this crude nested for loop seems to be a few times faster than using np.where
    output = np.zeros((h, w), dtype=np.bool)
    for y in range(h):
        for x in range(w):
            if noise[y, x] < img[y, x]:
                output[y, x] = True
    return output


@cc.export("ordered_dither", "f4[:,:](f4[:,:], f8[:,:])")
def ordered_dither(img, matrix):
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


@cc.export("ordered_dither_p", "f4[:,:](f4[:,:], f8, f8[:,:])")
def ordered_dither_p(img, pert, matrix):
    n = matrix.shape[0]
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            pixel = img[y, x]
            j = y % n
            if not (pixel == 0 or pixel == 1):
                i = x % n
                if matrix[j, i] + np.random.normal(0, pert) > img[y, x]:
                    img[y, x] = 0
                else:
                    img[y, x] = 1

    return img


# ERROR DIFFUSION FUNCTIONS. At some point EDOFDs should be added
@cc.export("ed_float", "f4[:,:](f4[:,:], f8[:,:], f4)")
def ed_float(img, kernel, str_value):
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


@cc.export("ed", "b1[:,:](u2[:,:], f8[:,:], f4)")
def ed(img_u16, kernel, str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/hopfer/core/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused.
    """
    # Converting to int32 allows for negative error accumulation while being faster than float.
    img = img_u16.astype(np.int32)
    height, width = img.shape

    # iterating over aranges seems much faster than the python range() for big arrays. tried using ndenumerate but it was slower and flatiter but it isn't fully supported.
    h, w = np.arange(height), np.arange(width)

    kernel_height, kernel_width = kernel.shape[0], kernel.shape[1]
    kernel_center_x, kernel_center_y = kernel_width // 2, kernel_height // 2

    output = np.zeros((height, width), dtype=np.bool)

    THRESHOLD = 32768

    for y in h:
        for x in w:
            old_pixel = img[y, x]

            if old_pixel >= THRESHOLD:
                new_pixel = 65535
                output[y, x] = True
            else:
                new_pixel = 0

            error = (old_pixel - new_pixel) * str_value

            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if (
                        kernel[ky, kx] != 0
                        # check if there is something at the index to diffuse. this led to the biggest improvement in speed.
                        and 0 <= y + ky - kernel_center_y < height
                        and 0 <= x + kx - kernel_center_x < width
                    ):  # check if the pixel is even inside the image. I've tried padding the image to avoid this check but it didn't seem to matter at all.
                        # Add the error to the int32 array
                        img[y + ky - kernel_center_y, x + kx - kernel_center_x] += (
                            np.int32(error * kernel[ky, kx])
                        )
                        # actually diffuse the error maybe the index could be precomputed

    return output  # return the image in a dithered form


# Same as above SERPENTINE
@cc.export("eds_float", "f4[:,:](f4[:,:], f8[:,:], f4)")
def eds_float(img, kernel, str_value):
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
                        # actually diffuse the error. maybe the index could be precomputed
    # Flip it one last time if needed
    if h.size % 2 != 0:
        img = np.fliplr(img)

    return img  # return the image in a dithered form


@cc.export("eds", "b1[:,:](u2[:,:], f8[:,:], f8)")
def eds_u16(img_u16, kernel, str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused. This is the serpentine version. It was separated for performance reasons.
    """

    img = img_u16.astype(np.int32)
    height, width = img.shape

    # iterating over aranges seems much faster than the python range() for big arrays. tried using ndenumerate but it was slower and flatiter but it isn't fully supported.
    h, w = np.arange(height), np.arange(width)

    kernel_height, kernel_width = kernel.shape[0], kernel.shape[1]
    kernel_center_x, kernel_center_y = kernel_width // 2, kernel_height // 2

    # Pre-allocate the boolean output
    output = np.zeros((height, width), dtype=np.bool_)

    # Midpoint for uint16 range (65535)
    THRESHOLD = 32768

    for y in h:
        # flipping the whole image seems like an easy way to do a serpentine raster.
        img = np.fliplr(img)
        # We must also flip the output view for this row so we write to the correct coordinate
        output = np.fliplr(output)

        for x in w:
            old_pixel = img[y, x]

            if old_pixel >= THRESHOLD:
                new_pixel = 65535
                output[y, x] = True
            else:
                new_pixel = 0

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
                            np.int32(error * kernel[ky, kx])
                        )
                        # actually diffuse the error. maybe the index could be precomputed

    # Flip back once at the end if we finished on an odd row to restore original orientation
    if h.size % 2 != 0:
        output = np.fliplr(output)

    return output  # return the image in a dithered form


@cc.export("sierra24a", "b1[:,:](u2[:,:], f8, b1)")
def sierra24a(img_u16, str_value, serpentine):
    # Hardcoding Sierra2 4A just for fun, it fast even with kernel looping.
    h, w = img_u16.shape
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768

    for y in range(h):
        # fliplr seems to be just as fast as reversing the index
        if serpentine:
            img = np.fliplr(img)
            output = np.fliplr(output)

        for x in range(w):
            old_value = img[y, x]

            if old_value >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = np.int32((old_value - new_value) * str_value)

            # as the sum of the kernel is 4, bitshifts were used.

            # current row
            if x + 1 < w:
                img[y, x + 1] += error >> 1  # x + 1

            # row + 1
            if y + 1 < h:
                img[y + 1, x] += error >> 2  # current x
                if x - 1 >= 0:
                    img[y + 1, x - 1] += error >> 2  # x - 1

    if serpentine:
        if h % 2 != 0:
            output = np.fliplr(output)

    return output


@cc.export("ostromoukhov_float", "f4[:,:](f4[:,:], f8[:,:], f8)")
def ostromoukhov_float(img, coeff_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value)
            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]

    return img


@cc.export("ostromoukhov", "b1[:,:](u2[:,:], f8[:,:], f8)")
def ostromoukhov_u16(img_u16, coeff_array, str_value):
    h, w = img_u16.shape
    # temporary promotion to int32 so that error could accumulate
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    # midgray of uint16
    THRESHOLD = 32768

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]

            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            coeff_values = coeff_array[coeff_idx]

            if old_value >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = (old_value - new_value) * str_value

            if x + 1 < w:
                img[y, x + 1] += np.int32(error * coeff_values[0])
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += np.int32(error * coeff_values[1])
            if y + 1 < h:
                img[y + 1, x] += np.int32(error * coeff_values[2])

    return output


@cc.export("ostromoukhov_s_float", "f4[:,:](f4[:,:], f8[:,:], f8)")
def ostromoukhov_s(img, coeff_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value)
            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]

        img = np.fliplr(img)

    if h % 2 != 0:
        img = np.fliplr(img)
    return img


@cc.export("ostromoukhov_s", "b1[:,:](u2[:,:], f8[:,:], f8)")
def ostromoukhov_s_u16(img_u16, coeff_array, str_value):
    h, w = img_u16.shape
    # Promotion to int32 for precise error accumulation
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768

    for y in range(h):
        img = np.fliplr(img)
        output = np.fliplr(output)

        for x in range(w):
            old_value = img[y, x]

            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            coeff_values = coeff_array[coeff_idx]

            if old_value >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = (old_value - new_value) * str_value

            if x + 1 < w:
                img[y, x + 1] += np.int32(error * coeff_values[0])
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += np.int32(error * coeff_values[1])
            if y + 1 < h:
                img[y + 1, x] += np.int32(error * coeff_values[2])

    if h % 2 != 0:
        output = np.fliplr(output)

    return output


@cc.export("zhou_fang_float", "f4[:,:](f4[:,:], f8[:,:], f8[:], f8)")
def zhou_fang_float(img, coeff_array, pert_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            pert = np.float64(np.random.uniform(0, 0.5))
            pert_mod = pert * pert_array[coeff_idx]
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value + pert_mod)
            img[y, x] = new_value
            error = (old_value - new_value) * str
            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]
    return img


@cc.export("zhou_fang", "b1[:,:](u2[:,:], f8[:,:], f8[:], f8)")
def zhou_fang_slow(img_u16, coeff_array, pert_array, str_value):
    h, w = img_u16.shape
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]

            # as the proposed algorithm works with uint8 we just bitshift the value of the current pixel to get the corrsponding 8bit values.
            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            # using xorshift and other faster generator produced terrible results, so thats what it is. its slow as hell, but images look fine.
            # TODO: look for a better way of generating the randomness
            pert = np.random.uniform() * THRESHOLD
            pert_mod = np.int32(pert * pert_array[coeff_idx])

            coeff_values = coeff_array[coeff_idx]

            if (old_value + pert_mod) >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = (old_value - new_value) * str_value
            e_int = np.int32(error)

            if x + 1 < w:
                img[y, x + 1] += np.int32(e_int * coeff_values[0])
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += np.int32(e_int * coeff_values[1])
            if y + 1 < h:
                img[y + 1, x] += np.int32(e_int * coeff_values[2])

    return output


@cc.export("zhou_fang_s_float", "f4[:,:](f4[:,:], f8[:,:], f8[:], f8)")
def zhou_fang_s_float(img, coeff_array, pert_array, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            coeff_idx = min(int(old_value * 255), 255)
            pert = np.float64(np.random.uniform(0, 0.5))
            pert_mod = pert * pert_array[coeff_idx]
            coeff_values = coeff_array[coeff_idx]
            new_value = np.round(old_value + pert_mod)
            img[y, x] = new_value
            error = (old_value - new_value) * str
            if x + 1 < w:
                img[y, x + 1] += error * coeff_values[0]
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += error * coeff_values[1]
            if y + 1 < h:
                img[y + 1, x] += error * coeff_values[2]
        img = np.fliplr(img)

    if h % 2 != 0:
        img = np.fliplr(img)
    return img


@cc.export("zhou_fang_s", "b1[:,:](u2[:,:], f8[:,:], f8[:], f8)")
def zhou_fang_s_slow(img_u16, coeff_array, pert_array, str_value):
    h, w = img_u16.shape
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768

    for y in range(h):
        img = np.fliplr(img)
        output = np.fliplr(output)

        for x in range(w):
            old_value = img[y, x]

            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            # using xorshift and other faster generator produced terrible results, so thats what it is. its slow as hell, but images look fine.
            # TODO: look for a better way of generating the randomness
            pert = np.random.uniform() * THRESHOLD
            pert_mod = np.int32(pert * pert_array[coeff_idx])

            coeff_values = coeff_array[coeff_idx]

            if (old_value + pert_mod) >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = (old_value - new_value) * str_value
            e_int = np.int32(error)

            if x + 1 < w:
                img[y, x + 1] += np.int32(e_int * coeff_values[0])
            if (x - 1 >= 0) and (y + 1 < h):
                img[y + 1, x - 1] += np.int32(e_int * coeff_values[1])
            if y + 1 < h:
                img[y + 1, x] += np.int32(e_int * coeff_values[2])

    if h % 2 != 0:
        output = np.fliplr(output)

    return output


@cc.export("zhou_fang_fast", "b1[:,:](u2[:,:], f8[:,:], f8[:], f8)")
def zhou_fang_fast(img_u16, coeff_array, pert_array, str_value):
    h, w = img_u16.shape
    img = (img_u16 >> 2).astype(np.int16)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 8192
    mcg_state = np.uint64(0xCAFEF00DD15EA5E5)
    MULT = np.uint64(6364136223846793005)

    fwd = np.arange(w, dtype=np.uint16)

    c0_table = coeff_array[:, 0] * str_value
    c1_table = coeff_array[:, 1] * str_value
    c2_table = coeff_array[:, 2] * str_value

    for y in range(h):
        for x in fwd:
            # Generate a random float using pcg32_fast (https://en.wikipedia.org/wiki/Permuted_congruential_generator)
            # This seems to be almost twice as fast as numpy's random module and produces noise that to me looks just as nice.

            x_bits = mcg_state

            count = np.uint32(x_bits >> np.uint32(61))

            # advance
            mcg_state = x_bits * MULT

            x_bits ^= x_bits >> np.uint32(22)

            rng_val_u32 = np.uint32(x_bits >> (np.uint32(22) + count))

            # getting the random number as a float seems to be just as fast, then again i think its cleaner to just get the in the range we already nee it.
            # rand_float = np.float64(rng_val_u32) * 2.3283064365386963e-10
            pert = rng_val_u32 >> 17

            old_value = img[y, x]

            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            pert_mod = np.int32(pert * pert_array[coeff_idx])

            if (old_value + pert_mod) >= THRESHOLD:
                new_value = 16383
                output[y, x] = True
            else:
                new_value = 0

            error = np.int32(old_value - new_value)
            c0 = c0_table[coeff_idx]
            c1 = c1_table[coeff_idx]
            c2 = c2_table[coeff_idx]

            if x + 1 < w:
                img[y, x + 1] += np.int32(error * c0)
            if x - 1 >= 0 and y + 1 < h:
                img[y + 1, x - 1] += np.int32(error * c1)
            if y + 1 < h:
                img[y + 1, x] += np.int32(error * c2)

    return output


@cc.export("zhou_fang_fast_s", "b1[:,:](u2[:,:], f8[:,:], f8[:], f8)")
def zhou_fang_fast_s(img_u16, coeff_array, pert_array, str_value):
    h, w = img_u16.shape
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768
    mcg_state = np.uint64(0xCAFEF00DD15EA5E5)
    MULT = np.uint64(6364136223846793005)

    fwd = np.arange(w, dtype=np.uint16)
    rev = fwd[::-1].copy()  # Ensure it's a contiguous array for speed

    c0_table = coeff_array[:, 0]
    c1_table = coeff_array[:, 1]
    c2_table = coeff_array[:, 2]

    for y in range(h):
        reverse = (y & 1) == 0
        indices = rev if reverse else fwd

        for x in indices:
            # Generate a random float using pcg32_fast (https://en.wikipedia.org/wiki/Permuted_congruential_generator)
            # This seems to be almost twice as fast as numpy's random module and produces noise that to me looks just as nice.

            x_bits = mcg_state

            count = np.uint32(x_bits >> np.uint32(61))

            # advance
            mcg_state = x_bits * MULT

            x_bits ^= x_bits >> np.uint32(22)

            rng_val_u32 = np.uint32(x_bits >> (np.uint32(22) + count))

            # getting the random number as a float seems to be just as fast, then again i think its cleaner to just get the in the range we already nee it.
            # rand_float = np.float64(rng_val_u32) * 2.3283064365386963e-10
            pert = rng_val_u32 >> 17

            old_value = img[y, x]

            coeff_idx = old_value >> 8
            if coeff_idx < 0:
                coeff_idx = 0
            elif coeff_idx > 255:
                coeff_idx = 255

            pert_mod = np.int32(pert * pert_array[coeff_idx])

            if (old_value + pert_mod) >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = (old_value - new_value) * str_value
            e_int = np.int32(error)
            c0 = c0_table[coeff_idx]
            c1 = c1_table[coeff_idx]
            c2 = c2_table[coeff_idx]

            if not reverse:
                if x + 1 < w:
                    img[y, x + 1] += np.int32(e_int * c0)
                if x - 1 >= 0 and y + 1 < h:
                    img[y + 1, x - 1] += np.int32(e_int * c1)
            else:
                if x - 1 >= 0:
                    img[y, x - 1] += np.int32(e_int * c0)
                if x + 1 < w and y + 1 < h:
                    img[y + 1, x + 1] += np.int32(e_int * c1)

            # Vertical always uses c2
            if y + 1 < h:
                img[y + 1, x] += np.int32(e_int * c2)

    return output


@cc.export("nakano", "b1[:,:](u2[:,:], f8, f8, b1)")
def nakano(img_u16, str_value, hysteresis_c, serpentine):
    # Nakano was so slow using loops through the kernel, that i decided to just hardcode it. this ways it dropped from 2.5s for 25mp image to about 0.5s
    h, w = img_u16.shape
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768

    for y in range(h):
        # fliplr seems to be just as fast as reversing the index
        if serpentine:
            img = np.fliplr(img)
            output = np.fliplr(output)

        for x in range(w):
            old_value = img[y, x]

            hysteresis = 0

            if hysteresis_c > 0:
                # using rotated Floyd-Steinberg kernel
                # precomputed constants for the maximum uint16 value
                VAL_7 = 28671  # (65535 * 7) >> 4
                VAL_5 = 20479  # (65535 * 5) >> 4
                VAL_3 = 12287  # (65535 * 3) >> 4
                VAL_1 = 4095  # 65535 >> 4

                # current row
                if x - 1 >= 0:
                    if output[y, x - 1]:
                        hysteresis += VAL_7  # x - 1

                # row above
                if y - 1 >= 0:
                    if output[y - 1, x]:
                        hysteresis += VAL_5  # current x
                    if x - 1 >= 0:
                        if output[y - 1, x - 1]:
                            hysteresis += VAL_1  # x - 1
                    if x + 1 < w:
                        if output[y - 1, x + 1]:
                            hysteresis += VAL_3  # x + 1

            hysteresis = np.int32(hysteresis * hysteresis_c)

            if old_value + hysteresis >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = np.int32((old_value - new_value) * str_value)

            # as the sum of the kernel is 64, bitshifts were used. this shaved about 0.1s from the execution. i'm sorry if someone ever reads the following:

            # current row
            if x + 2 < w:
                img[y, x + 2] += (error * 6) >> 6  # x + 2
            if x + 3 < w:
                img[y, x + 3] += (error * 4) >> 6  # x + 3

            # row + 1
            if y + 1 < h:
                if x - 2 >= 0:
                    img[y + 1, x - 2] += (error * 1) >> 6  # x - 2
                if x - 1 >= 0:
                    img[y + 1, x - 1] += (error * 6) >> 6  # x - 1
                if x + 2 < w:
                    img[y + 1, x + 2] += (error * 5) >> 6  # x + 2
                if x + 3 < w:
                    img[y + 1, x + 3] += (error * 3) >> 6  # x + 3

            # row + 2
            if y + 2 < h:
                if x - 1 >= 0:
                    img[y + 2, x - 1] += (error * 4) >> 6  # x - 1
                # no checks, x is directly bellow
                img[y + 2, x] += (error * 7) >> 6
                if x + 1 < w:
                    img[y + 2, x + 1] += (error * 3) >> 6  # x + 1
                if x + 2 < w:
                    img[y + 2, x + 2] += (error * 5) >> 6  # x + 2
                if x + 3 < w:
                    img[y + 2, x + 3] += (error * 3) >> 6  # x + 3

            # row + 3
            if y + 3 < h:
                if x - 1 >= 0:
                    img[y + 3, x - 1] += (error * 3) >> 6  # x - 1
                # no checks, same reason
                img[y + 3, x] += (error * 5) >> 6
                if x + 1 < w:
                    img[y + 3, x + 1] += (error * 3) >> 6  # x + 1
                if x + 2 < w:
                    img[y + 3, x + 2] += (error * 4) >> 6  # x + 2
                if x + 3 < w:
                    img[y + 3, x + 3] += (error * 2) >> 6  # x + 3

    if serpentine:
        if h % 2 != 0:
            output = np.fliplr(output)

    return output


@cc.export("levien_float", "f4[:,:](f4[:,:], f8, f8)")
def levien_float(img, hysteresis_c, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            hysteresis = 0

            if x - 1 >= 0:
                hysteresis += img[y, x - 1] * 0.5 * hysteresis_c
            if y - 1 >= 0:
                hysteresis += img[y - 1, x] * 0.5 * hysteresis_c

            if old_value + hysteresis > 0.5:
                new_value = 1
            else:
                new_value = 0

            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * 0.5
            if y + 1 < h:
                img[y + 1, x] += error * 0.5

    return img


@cc.export("levien_s", "f4[:,:](f4[:,:], f8, f8)")
def levien_s(img, hysteresis_c, str):
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old_value = img[y, x]
            hysteresis = 0

            if x - 1 >= 0:
                hysteresis += img[y, x - 1] * 0.5 * hysteresis_c
            if y - 1 >= 0:
                hysteresis += img[y - 1, x] * 0.5 * hysteresis_c

            if old_value + hysteresis > 0.5:
                new_value = 1
            else:
                new_value = 0

            img[y, x] = new_value
            error = (old_value - new_value) * str

            if x + 1 < w:
                img[y, x + 1] += error * 0.5
            if y + 1 < h:
                img[y + 1, x] += error * 0.5

        img = np.fliplr(img)

    if h % 2 != 0:
        img = np.fliplr(img)
    return img


@cc.export("levien", "b1[:,:](u2[:,:], f8, f8, b1)")
def levien(img_u16, str_value, hysteresis_c, serpentine):
    # Nakano was so slow using loops through the kernel, that i decided to just hardcode it. this ways it dropped from 2.5s for 25mp image to about 0.5s
    h, w = img_u16.shape
    img = img_u16.astype(np.int32)
    output = np.zeros((h, w), dtype=np.bool)

    THRESHOLD = 32768
    HVAL = 65535 >> 1  # this is the value of the hysteresis per pixel

    for y in range(h):
        # fliplr seems to be just as fast as reversing the index
        if serpentine:
            img = np.fliplr(img)
            output = np.fliplr(output)

        for x in range(w):
            old_value = img[y, x]

            hysteresis = 0

            # get the hysteresis value here. if hysteresis is 0 there is absolutely no need to hit these indeces up and waste time.

            if hysteresis_c != 0:
                # current row
                if x - 1 >= 0 and output[y, x - 1]:
                    hysteresis += HVAL  # x - 1

                # row above
                if y - 1 >= 0 and output[y - 1, x]:
                    hysteresis += HVAL  # current x

            hysteresis = np.int32(hysteresis * hysteresis_c)

            if old_value + hysteresis >= THRESHOLD:
                new_value = 65535
                output[y, x] = True
            else:
                new_value = 0

            error = np.int32((old_value - new_value) * str_value)

            # as the sum of the kernel is 2, bitshifts were used.

            # current row
            if x + 1 < w:
                img[y, x + 1] += error >> 1  # x + 1

            # row bellow
            if y + 1 < h:
                img[y + 1, x] += error >> 1

    if serpentine:
        if h % 2 != 0:
            output = np.fliplr(output)

    return output


# GRAYSCALE CONVERSION functions follow.
@cc.export("luminance", "u2[:,:](u2[:,:,:])")
def luminance(img):
    h, w, _ = img.shape
    out = np.zeros((h, w), dtype=np.uint16)

    for y in range(h):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
            out[y, x] = np.uint16(luma + 0.5)

    return out


@cc.export("luma", "u2[:,:](u2[:,:,:])")
def luma(img):
    h, w, _ = img.shape
    out = np.zeros((h, w), dtype=np.uint16)

    for y in range(h):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            luma_val = 0.299 * r + 0.587 * g + 0.114 * b
            out[y, x] = np.uint16(luma_val + 0.5)

    return out


@cc.export("average", "u2[:,:](u2[:,:,:])")
def average(img):
    h, w, _ = img.shape
    out = np.zeros((h, w), dtype=np.uint16)

    for y in range(h):
        for x in range(w):
            r = np.uint32(img[y, x, 0])
            g = np.uint32(img[y, x, 1])
            b = np.uint32(img[y, x, 2])

            out[y, x] = np.uint16((r + g + b + 1) // 3)

    return out


@cc.export("value", "u2[:,:](u2[:,:,:])")
def value(img):
    h, w, _ = img.shape
    out = np.zeros((h, w), dtype=np.uint16)

    for y in range(h):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            out[y, x] = max(r, g, b)

    return out


@cc.export("lightness", "u2[:,:](u2[:,:,:])")
def lightness(img):
    h, w, _ = img.shape
    out = np.zeros((h, w), dtype=np.uint16)

    for y in range(h):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            mx = max(r, g, b)
            mn = min(r, g, b)

            out[y, x] = np.uint16((np.uint32(mx) + mn + 1) // 2)

    return out


@cc.export("manual", "u2[:,:](u2[:,:,:], f8, f8, f8)")
def manual(img, rf, gf, bf):
    h, w, _ = img.shape
    rf_32 = np.float32(rf)
    gf_32 = np.float32(gf)
    bf_32 = np.float32(bf)

    out = np.zeros((h, w), dtype=np.uint16)

    for y in range(h):
        for x in range(w):
            r = img[y, x, 0]
            g = img[y, x, 1]
            b = img[y, x, 2]

            val = rf_32 * r + gf_32 * g + bf_32 * b

            if val > 65535.0:
                val = 65535.0
            elif val < 0.0:
                val = 0.0

            out[y, x] = np.uint16(val)

    return out


# The IMAGE PROCESSING fuctions should go here if i decide to implement them from scratch instead of using pillow
@cc.export("sharpen", "f4[:,:](f4[:,:],f8)")
def sharpen(image, str=1.0):
    str *= 0.1
    x = str + 1.0
    y = -str / 4

    # A classic sharpening kernel found on wiki
    kernel = np.array([[0, y, 0], [y, x, y], [0, y, 0]]).astype(np.float32)

    # Create a padded image to avoid out of bounds error
    padded_image = np.zeros((image.shape[0] + 2, image.shape[1] + 2), dtype=np.float32)
    padded_image[1:-1, 1:-1] = image

    sharpened = np.zeros((image.shape[0], image.shape[1]), dtype=np.float32)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded_image[i : i + 3, j : j + 3]  # Extract the 3x3 region
            sharpened[i, j] = np.sum(region * kernel)  # Apply the kernel

    return sharpened


cc.compile()
