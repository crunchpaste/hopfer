from PIL import Image
import numpy as np
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap

def pixmap_to_numpy(pixmap):
    image = pixmap.toImage()
    pil_image = Image.fromqpixmap(image)
    pil_image.convert("L")
    image_array = np.array(pil_image) / 255

    return image_array

def numpy_to_pixmap(image_array):
    if image_array.dtype != np.uint8:
        image_array = (image_array * 255).clip(0, 255).astype(np.uint8)
    pil_image = Image.fromarray(image_array)
    pil_image.convert("RGBA")
    qimage = ImageQt(pil_image)
    pixmap = QPixmap.fromImage(qimage)

    return pixmap
