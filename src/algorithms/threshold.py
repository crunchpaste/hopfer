import numpy as np
from numba import njit, prange

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

@njit(cache=True)
def thresh(img, threshold_value):
    # As simple as it gets :)
    # Slightly (about 15%) improves performace when in njit. Unfortunately slightly slower in static.
    t = threshold_value - 0.5
    img = np.rint(img + t)
    return img

def niblack_threshold(img, settings):
    block_size = int(settings["block_size"])
    k = settings["k_factor"] / 100
    return niblack(img, block_size, k)

@njit(cache=True)
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
                integral_img[y2, x2]      # Bottom right
                - integral_img[y2, x1]    # Left
                - integral_img[y1, x2]    # Top
                + integral_img[y1, x1]    # Top left
            )

            block_sq_sum = (
                squared_integral_img[y2, x2]      # Bottom right
                - squared_integral_img[y2, x1]    # Left
                - squared_integral_img[y1, x2]    # Top
                + squared_integral_img[y1, x1]    # Top left
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
            threshold = (mean - k * std)

            # Check against the calculated threshold
            if img[y, x] > threshold:
                output_img[y, x] = 1
            else:
                output_img[y, x] = 0

    return output_img


def sauvola_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"] / 100
    k = settings["k_factor"] / 100
    return sauvola(img, block_size, dynamic_range, k)

@njit(cache=True)
def sauvola(img, n=25, R=0.5, k=0.2):
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
                integral_img[y2, x2]      # Bottom right
                - integral_img[y2, x1]    # Left
                - integral_img[y1, x2]    # Top
                + integral_img[y1, x1]    # Top left
            )

            block_sq_sum = (
                squared_integral_img[y2, x2]      # Bottom right
                - squared_integral_img[y2, x1]    # Left
                - squared_integral_img[y1, x2]    # Top
                + squared_integral_img[y1, x1]    # Top left
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

def phansalkar_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"] / 100
    k = settings["k_factor"] / 100
    p = settings["p_factor"] / 100
    q = settings["q_factor"] / 10

    return phansalkar(img, block_size, dynamic_range, k, p, q)

@njit(cache=True)
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
                integral_img[y2, x2]      # Bottom right
                - integral_img[y2, x1]    # Left
                - integral_img[y1, x2]    # Top
                + integral_img[y1, x1]    # Top left
            )

            block_sq_sum = (
                squared_integral_img[y2, x2]      # Bottom right
                - squared_integral_img[y2, x1]    # Left
                - squared_integral_img[y1, x2]    # Top
                + squared_integral_img[y1, x1]    # Top left
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
