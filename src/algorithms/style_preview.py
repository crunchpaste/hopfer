import numpy as np
from numba import njit

"""
I've tried improving this function in numerous ways a it is purely aesthetic and does nothing important. I've tried using prange, though it seems that the overhead of parallelisation is more important than the actual improvement achieved by it. Also tried assigning x,y as a whole, whick gave slightly worse results. The static version is also about 10% slower that the njitted one.
"""


@njit
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


@njit
def alpha_composite(img, alpha, alpha_color):
    h, w, _ = img.shape
    output_img = np.zeros((h, w, 3), dtype=np.uint8)

    alpha_r = alpha_color[0]
    alpha_g = alpha_color[1]
    alpha_b = alpha_color[2]

    for y in range(h):
        for x in range(w):
            pixel = img[y, x]
            alpha_pixel = alpha[y, x]

            output_r = alpha_pixel * pixel[0] + (1 - alpha_pixel) * alpha_r
            output_g = alpha_pixel * pixel[1] + (1 - alpha_pixel) * alpha_g
            output_b = alpha_pixel * pixel[2] + (1 - alpha_pixel) * alpha_b

            output_r = max(0, min(255, output_r))
            output_g = max(0, min(255, output_g))
            output_b = max(0, min(255, output_b))

            output_img[y, x, 0] = output_r
            output_img[y, x, 1] = output_g
            output_img[y, x, 2] = output_b

    return output_img


# def alpha_composite(foreground, background, alpha):
#     # Ensure alpha is in [0, 1] range
#     alpha = alpha / 255.0  # Convert from [0, 255] to [0, 1]

#     # Create empty output image
#     output = np.zeros_like(background)

#     # Apply alpha blending for each color channel
#     for y in range(foreground.shape[0]):
#         for x in range(foreground.shape[1]):
#             # Get foreground and background color at each pixel
#             fg_pixel = foreground[y, x]
#             bg_pixel = background[y, x]

#             # Alpha blending formula for each color channel (R, G, B)
#             output[y, x, 0] = alpha * fg_pixel[0] + (1 - alpha) * bg_pixel[0]  # Red channel
#             output[y, x, 1] = alpha * fg_pixel[1] + (1 - alpha) * bg_pixel[1]  # Green channel
#             output[y, x, 2] = alpha * fg_pixel[2] + (1 - alpha) * bg_pixel[2]  # Blue channel

#     return output
