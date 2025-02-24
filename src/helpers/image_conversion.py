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

    print(f"DEPTH: {qimage.depth()}")

    arr = np.frombuffer(mem_view.tobytes(), dtype=np.uint8)

    # we get the channels by dividing the length by the pixel count
    channels = arr.shape[0] // (width * height)

    # reshape it to its proper size
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


def numpy_to_pixmap(img_array, alpha=None):
    # A bit of a spaghetti monster, but alpha is only passed when the image
    # is stored into the clipboard, if that makes sense.

    h, w = img_array.shape[:2]
    c = 1 if img_array.ndim == 2 else img_array.shape[2]
    image_array = np.copy(img_array)

    if alpha is not None:
        alpha_array = np.copy(alpha)
        c += 1
        if alpha_array.dtype != np.uint8:
            alpha_array = (alpha_array * 255).clip(0, 255).astype(np.uint8)
    else:
        alpha_array = np.full((h, w), 255, dtype=np.uint8)

    if image_array.dtype != np.uint8:
        # This one is quite slow for large images and definitely needs improvement
        image_array = (image_array * 255).clip(0, 255).astype(np.uint8)
    if alpha_array.dtype != np.uint8:
        # This one is quite slow for large images and definitely needs improvement
        alpha_array = (alpha_array * 255).clip(0, 255).astype(np.uint8)

    if image_array.ndim == 2 and alpha is None:
        # This is the case only when the halftoning mode is None
        format = QImage.Format_Grayscale8
        h, w = image_array.shape
        c = 1

    elif image_array.ndim == 3 or alpha is not None:
        if c == 2:
            # This is grayscale with alpha
            # For some reason QImage does not support LA so this is needed
            image_array = np.dstack(
                (
                    image_array,
                    image_array,
                    image_array,
                    alpha_array,
                )
            )
            format = QImage.Format_RGBA8888
            c = 4
        elif c == 3:
            # This is RGB without alpha. Just adapt the format
            format = QImage.Format_RGB888
        elif c == 4:
            # This is RGB with alpha. Just adapt the format
            format = QImage.Format_RGBA8888

    bytes = c * w
    qimage = QImage(image_array, w, h, bytes, format)
    # TODO: Should check how to create the pixmap directly from an array
    pixmap = QPixmap.fromImage(qimage)

    return pixmap
