from PIL import Image
import numpy as np
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap, QImage

import time

def pixmap_to_numpy(pixmap):
    image = pixmap.toImage()
    pil_image = Image.fromqpixmap(image)
    pil_image.convert("L")
    image_array = np.array(pil_image) / 255

    return image_array

def numpy_to_pixmap(img_array):

    image_array = np.copy(img_array)
    if image_array.dtype != np.uint8:
        # This one is quite slow for large images and definitely needs improvement
        image_array = (image_array * 255).clip(0, 255).astype(np.uint8)
    if image_array.ndim == 2:
        # This is the case only when the halftoning mode is None
        format = QImage.Format_Grayscale8
        h, w = image_array.shape
        c = 1
    elif image_array.ndim == 3:
        h, w, c = image_array.shape
        if c == 2:
            # This is grayscale with alpha
            # For some reason QImage does not support LA so this is needed
            image_array = np.dstack((
                image_array,
                image_array,
                image_array,
                np.full((h, w), 255, dtype=np.uint8)
            ))
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
