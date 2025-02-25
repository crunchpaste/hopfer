import numpy as np
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap


def qimage_to_numpy(qimage):
    # this is a very, very hacky way to get the clipboard image data
    # without encoding it as a .png first, but its magnitudes faster

    # these are simple to get
    width, height = qimage.width(), qimage.height()

    # it seems that .bits() returns a memview, which could be used to
    # create a numpy array
    mem_view = qimage.bits()

    arr = np.frombuffer(mem_view.tobytes(), dtype=np.uint8)

    # we get the channels by dividing the length by the pixel count
    channels = arr.shape[0] // (width * height)
    # reshape it to its proper size
    if channels == 1:
        arr = arr.reshape(height, width)
    else:
        arr = arr.reshape((height, width, channels))
    return arr


def pixmap_to_numpy(pixmap):
    image = pixmap.toImage()
    pil_image = Image.fromqpixmap(image)
    pil_image.convert("L")
    image_array = np.array(pil_image) / 255

    return image_array


def boolean_pixmap(img_array, light, dark):
    h, w = img_array.shape
    img = img_array.astype(np.uint8) * 255

    qimage = QImage(img, w, h, w, QImage.Format_Grayscale8)
    print(qimage.bytesPerLine())
    qimage.convertToFormat_inplace(QImage.Format_Mono, Qt.AutoColor)
    print(qimage)
    pixmap = QPixmap.fromImage(qimage)

    return pixmap


def numpy_to_pixmap(img_array, alpha=None, qi=False):
    # Converts a NumPy array to a QPixmap or QImage.
    # A bit of a spaghetti monster, but alpha is only passed when the image
    # is stored into the clipboard, if that makes sense.

    h, w = img_array.shape[:2]
    c = 1 if img_array.ndim == 2 else img_array.shape[2]

    image_array = np.copy(img_array)

    # Handle alpha
    alpha_array = (
        _prepare_alpha(alpha, h, w)
        if alpha is not None
        else np.full((h, w), 255, dtype=np.uint8)
    )

    # Ensure the image is uint8. might be a bit slow.
    image_array = _convert_to_uint8(image_array)

    # Determine color format based on number of channels
    format, image_array = _determine_format(image_array, alpha_array, c, alpha)

    # Create QImage
    bytes_per_line = c * w
    qimage = QImage(image_array, w, h, bytes_per_line, format)

    if qi:
        return qimage  # Return qimage for clipboard purposes

    # TODO: Should check how to create the pixmap directly from an array
    return QPixmap.fromImage(qimage)


def _prepare_alpha(alpha, h, w):
    alpha_array = np.copy(alpha)
    if alpha_array.dtype != np.uint8:
        alpha_array = (alpha_array * 255).clip(0, 255).astype(np.uint8)
    return alpha_array


def _convert_to_uint8(image_array):
    if image_array.dtype != np.uint8:
        # This one is quite slow for large images and definitely needs improvement
        return (image_array * 255).clip(0, 255).astype(np.uint8)
    return image_array


def _determine_format(image_array, alpha_array, c, alpha):
    if image_array.ndim == 2 and alpha is None:
        # This is the case only when the halftoning mode is None
        return QImage.Format_Grayscale8, image_array

    if alpha is not None or image_array.ndim == 3:
        if c == 2:
            # This is grayscale with alpha
            # For some reason QImage does not support LA, so we need to expand to RGBA
            image_array = np.dstack(
                (image_array, image_array, image_array, alpha_array)
            )
            return QImage.Format_RGBA8888, image_array
        elif c == 3:
            return QImage.Format_RGB888, image_array  # RGB without alpha
        elif c == 4:
            return QImage.Format_RGBA8888, image_array  # RGB with alpha

    return QImage.Format_RGB888, image_array  # Fallback
