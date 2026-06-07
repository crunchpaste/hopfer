# sauvola.pxi
from libc.stdint cimport uint8_t, uint16_t
from libc.math cimport sqrt

def sauvola(img, uint16_t n=25, double R=0.5, double k=0.2):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef uint8_t[:, :] work_buf = np.array(img, dtype=np.uint8)
    # Scaling R internally to keep the UI the same
    cdef double R_scaled = R * 255.0 + 1
    # Compute the integral image and squared integral image
    cdef double[:, :] integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    cdef double[:, :] squared_integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    _sauvola_core(work_buf, out, integral_img, squared_integral_img, h, w, n, k, R_scaled)
    return out.view(np.bool_)

cdef void _sauvola_core(
    uint8_t[:, :] img,
    uint8_t[:, :] out,
    double[:, :] integral_img,
    double[:, :] squared_integral_img,
    int h, int w, int n, double k, double R_scaled
) noexcept nogil:
    cdef int y, x, y1, x1, y2, x2, w_half, block_area
    cdef double val, block_sum, block_sq_sum, mean, mean_sq, variance, std, threshold

    w_half = n // 2  # Half size of the block (window)

    # Build the integral images. This massively improves the perfomance especially at bigger window sizes. The concept is relatively new to me but seems to work. Wikipedia has it described quite well: https://en.wikipedia.org/wiki/Summed-area_table. This could probably be done just once and be stored in the ImageStorage class...
    for y in range(h):
        for x in range(w):
            val = <double>img[y, x]
            # The integral image, used for the mean of the block
            integral_img[y + 1, x + 1] = (
                integral_img[y + 1, x]   # Left
                + integral_img[y, x + 1] # Top
                - integral_img[y, x]     # Top left
                + val                    # Current
            )
            # The squared integral image, used for the std of the block
            squared_integral_img[y + 1, x + 1] = (
                squared_integral_img[y + 1, x]   # Left
                + squared_integral_img[y, x + 1] # Top
                - squared_integral_img[y, x]     # Top left
                + val * val                      # Current
            )

    for y in prange(h, schedule='static'):
        # There seems to be no significant improvement in perfomance if doing it in a prange.
        for x in range(w):
            # Boundary checks
            y1 = y - w_half if y - w_half > 0 else 0
            x1 = x - w_half if x - w_half > 0 else 0
            y2 = y + w_half + 1 if y + w_half + 1 < h else h
            x2 = x + w_half + 1 if x + w_half + 1 < w else w
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
            variance = mean_sq - mean * mean
            # if variance gets to be negative strange glitches start happening
            if variance <= 0:
                variance = 0
            std = sqrt(variance)
            # Get the threshold for the current pixel using the formula provided by craft of coding: https://craftofcoding.wordpress.com/2021/10/06/thresholding-algorithms-sauvola-local/
            threshold = mean * (1 + k * ((std / R_scaled) - 1))
            # Check against the calculated threshold
            if img[y, x] > threshold:
                out[y, x] = 1
            else:
                out[y, x] = 0
