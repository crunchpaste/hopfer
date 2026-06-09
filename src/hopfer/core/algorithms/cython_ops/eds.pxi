# eds.pxi
from libc.stdint cimport int32_t, uint8_t, uint16_t

def eds(img_u16, kernel, double str_value):
    """
    A generic error diffusion fuction. Expects the image, the kernel (see src/image_processor for example) and a strength of diffusion as a float between 0 and 1 which controls the amount of error to be diffused. This is the serpentine version. It was separated for performance reasons.
    """
    cdef int height = img_u16.shape[0]
    cdef int width = img_u16.shape[1]
    out = np.zeros((height, width), dtype=np.uint8)
    cdef int32_t[:, :] img = np.array(img_u16, dtype=np.int32)
    cdef double[:, :] kernel_buf = np.array(kernel, dtype=np.float64)
    cdef int kernel_height = kernel.shape[0]
    cdef int kernel_width = kernel.shape[1]
    _eds_core(img, kernel_buf, out, height, width, kernel_height, kernel_width, str_value)
    return out.view(np.bool_)

cdef void _eds_core(
    int32_t[:, :] img,
    double[:, :] kernel,
    uint8_t[:, :] out,
    int height, int width,
    int kernel_height, int kernel_width,
    double str_value
) noexcept nogil:
    cdef int y, x, ky, kx, kernel_center_x, kernel_center_y, ny, nx
    cdef int32_t old_pixel, new_pixel
    cdef double error
    cdef int32_t THRESHOLD = 32768
    cdef bint left_to_right

    kernel_center_x = kernel_width // 2
    kernel_center_y = kernel_height // 2

    for y in range(height):
        # flipping the whole image seems like an easy way to do a serpentine raster.
        left_to_right = (y % 2 == 0)
        for x in range(width):
            # map logical x to actual column depending on scan direction
            nx = x if left_to_right else (width - 1 - x)
            old_pixel = img[y, nx]
            if old_pixel >= THRESHOLD:
                new_pixel = 65535
                out[y, nx] = 1
            else:
                new_pixel = 0
                out[y, nx] = 0
            img[y, nx] = new_pixel  # replace the value in place
            error = (old_pixel - new_pixel) * str_value
            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    if kernel[ky, kx] != 0:
                        # check if there is something at the index to diffuse. this led to the biggest improvement in speed.
                        ny = y + ky - kernel_center_y
                        # mirror the kernel x offset on reverse rows so diffusion always points forward
                        if left_to_right:
                            nx = x + kx - kernel_center_x
                        else:
                            nx = (width - 1 - x) - kx + kernel_center_x
                        if 0 <= ny < height and 0 <= nx < width:
                            # check if the pixel is even inside the image. I've tried padding the image to avoid this check but it didn't seem to matter at all.
                            # Add the error to the int32 array
                            img[ny, nx] += <int32_t>(error * kernel[ky, kx])
                            # actually diffuse the error. maybe the index could be precomputed
