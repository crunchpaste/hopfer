# phansalkar.pxi
from libc.stdint cimport uint8_t, uint16_t
from libc.math cimport sqrt, exp

def phansalkar(img, uint16_t n=25, double R=0.5, double k=0.2, double p=3.0, double q=10.0):
    cdef int h = img.shape[0]
    cdef int w = img.shape[1]
    out = np.zeros((h, w), dtype=np.uint8)
    cdef uint8_t[:, :] work_buf = np.array(img, dtype=np.uint8)
    # Scale R to match uint8 range (0-255)
    cdef double R_scaled = R * 255.0
    if R_scaled <= 0:
        R_scaled = 1.0
    # Compute the integral image and squared integral image
    # Using float64 is mandatory for 24MP images to prevent overflow
    cdef double[:, :] integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    cdef double[:, :] squared_integral_img = np.zeros((h + 1, w + 1), dtype=np.float64)
    _phansalkar_core(work_buf, out, integral_img, squared_integral_img, h, w, n, k, p, q, R_scaled)
    return out.view(np.bool_)

cdef void _phansalkar_core(
    uint8_t[:, :] img,
    uint8_t[:, :] out,
    double[:, :] integral_img,
    double[:, :] squared_integral_img,
    int h, int w, int n, double k, double p, double q, double R_scaled
) noexcept nogil:
    cdef int y, x, y1, x1, y2, x2, w_half
    cdef double val, s, sq_s, area, mean, variance, std, threshold

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
                + (val * val)                    # Current
            )

    for y in range(h):
        # There seems to be no significant improvement in perfomance if doing it in a prange.
        for x in range(w):
            # Boundary checks
            y1 = y - w_half if y - w_half > 0 else 0
            x1 = x - w_half if x - w_half > 0 else 0
            y2 = y + w_half + 1 if y + w_half + 1 < h else h
            x2 = x + w_half + 1 if x + w_half + 1 < w else w
            area = <double>((y2 - y1) * (x2 - x1))
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
                std = sqrt(variance)
            # Get the threshold for the current pixel using the formula provided by craft of coding: https://craftofcoding.wordpress.com/2021/09/28/thresholding-algorithms-phansalkar-local/
            # Mean is divided by 255 to keep the exponential term consistent with the original 0.0-1.0 logic.
            threshold = mean * (
                1.0
                + p * exp(-q * (mean / 255.0))
                + k * ((std / R_scaled) - 1.0)
            )
            # Check against the calculated threshold
            if <double>img[y, x] > threshold:
                out[y, x] = 1
            else:
                out[y, x] = 0
