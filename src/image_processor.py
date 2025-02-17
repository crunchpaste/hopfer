import concurrent.futures

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from PySide6.QtCore import QCoreApplication, QObject, Signal

from helpers.decorators import queue

try:
    from algorithms.thresholdc import (
        niblack_threshold,
        phansalkar_threshold,
        sauvola_threshold,
        threshold,
    )
except ImportError:
    from algorithms.threshold import (
        niblack_threshold,
        phansalkar_threshold,
        sauvola_threshold,
        threshold,
    )

try:
    from algorithms.mezzoc import mezzo
except ImportError:
    from algorithms.mezzo import mezzo

try:
    from algorithms.bayerc import bayer
except ImportError:
    from algorithms.bayer import bayer

try:
    from algorithms.error_diffusionc import error_diffusion
except ImportError:
    from algorithms.error_diffusion import error_diffusion

try:
    from algorithms.static import average, lightness, luma, luminance, manual, value
except ImportError:
    from algorithms.grayscale import average, lightness, luma, luminance, manual, value

# try:
#     from algorithms.static import sharpen
# except ImportError:
#     pass


def worker(image, mode, im_settings, algorithm, settings, step=0):
    if step == 0:
        image = worker_g(image, mode)

    if step <= 1:
        image = worker_e(image, im_settings)

    processed_image = worker_h(image, algorithm, settings)
    return processed_image


def worker_g(image, mode, settings):
    """
    This is the worker for grayscale conversion. Currently it is just being terminated not quite gracefully, though it seems to not be a problem. This is the only way I've found for the GUI to not freeze while processing.
    """

    image = convert_to_grayscale(image, mode, settings)
    return image


def worker_e(image, im_settings):
    """
    This is the worker for image enchancements e.g. blurs. As with worker_g and worker_h it is just being terminated.
    """
    _brightness = im_settings["brightness"] / 100

    if _brightness > 0:
        # using a log function makes the adjustment feel a bit more natural
        _brightness = 5 * (np.log(1 + (0.01 - 1) * _brightness) / np.log(0.01))
    _brightness += 1
    _contrast = im_settings["contrast"] / 100
    if _contrast > 0:
        # using a log function makes the adjustment feel a bit more natural
        _contrast = 5 * (np.log(1 + (0.01 - 1) * _contrast) / np.log(0.01))
    _contrast += 1
    # _sharpness = im_settings["sharpness"]

    pil_needed = False
    converted = False  # if the image has already been converted back

    if im_settings["normalize"]:
        min_val = np.min(image)
        max_val = np.max(image)
        image = (image - min_val) / (max_val - min_val)

    if im_settings["equalize"]:
        hist, bins = np.histogram(image.flatten(), bins=256, range=[0, 1])

        cdf = hist.cumsum()
        cdf_normalized = cdf / cdf[-1]

        image = np.interp(image.flatten(), bins[:-1], cdf_normalized).reshape(
            image.shape
        )

    if im_settings["bc_t"] or im_settings["blur_t"] or im_settings["unsharp_t"] > 0:
        # if PIL manupulation is needed, convert to a PIL image once
        pil_needed = True

        _image = (image * 255).astype(np.uint8)
        pil_image = Image.fromarray(_image)

    if im_settings["bc_t"]:
        if _brightness != 1.0:
            # if PIL manupulation is needed, convert to a PIL image once
            pil_needed = True
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(_brightness)
        if _contrast != 1.0:
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(_contrast)
    if im_settings["blur_t"]:
        _blur = im_settings["blur"] / 10
        _median = int(im_settings["median"] * 2 - 1)
        if _blur > 0:
            pil_image = pil_image.filter(ImageFilter.GaussianBlur(_blur))
        if _median > 1:
            pil_image = pil_image.filter(ImageFilter.MedianFilter(_median))
    if im_settings["unsharp_t"]:
        radius = im_settings["u_radius"] / 10
        strenght = int(im_settings["u_strenght"] * 2)
        thresh = im_settings["u_thresh"]

        pil_image = pil_image.filter(ImageFilter.UnsharpMask(radius, strenght, thresh))
        # if _sharpness > 0:
        #     converted = True
        #     if pil_needed:
        #         _image = (np.array(pil_image) / 255).astype(np.float32)
        #     else:
        #         _image = image
        #     image = sharpen(_image, _sharpness)

    if not converted and pil_needed:
        # this will get the image back to a numpy array if it is not done already by the sharpness filter. should be removed when unsharp is implemented.
        image = (np.array(pil_image) / 255).astype(np.float32)
    return image


def worker_h(image, algorithm, settings):
    """
    This is the worker for halftoning. As with worker_g and worker_e it is just being terminated.
    """
    image = np.copy(image).astype(np.float32)
    processed_image = apply_algorithm(image, algorithm, settings)
    return processed_image


def convert_to_grayscale(image, mode, settings):
    """
    The function responsible for the grayscale conversion in the main worker_p.
    """

    if mode == "Luminance":
        return luminance(image)
    if mode == "Luma":
        return luma(image)
    elif mode == "Average":
        return average(image)
    elif mode == "Value":
        return value(image)
    elif mode == "Lightness":
        return lightness(image)
    elif mode == "Manual RGB":
        r = settings["r"] / 100
        g = settings["g"] / 100
        b = settings["b"] / 100
        return manual(image, r, g, b)
    else:
        return luminance(image)


def apply_algorithm(image, algorithm, settings):
    """
    Apply the selected halftoning algorithm to the image via worker_p.

    :param image: The original image as a NumPy array.
    :param settings: Settings for the algorithm (like threshold, dither levels).
    :return: The processed image as a NumPy array.
    """
    # Apply the chosen halftoning algorithm using the respective kernel
    if algorithm == "Fixed threshold":
        processed_image = threshold(image, settings)

    elif algorithm == "Niblack threshold":
        processed_image = niblack_threshold(image, settings)

    elif algorithm == "Sauvola threshold":
        processed_image = sauvola_threshold(image, settings)

    elif algorithm == "Phansalkar threshold":
        processed_image = phansalkar_threshold(image, settings)

    elif algorithm == "Mezzotint uniform":
        processed_image = mezzo(image, settings, mode="uniform")

    elif algorithm == "Mezzotint normal":
        processed_image = mezzo(image, settings, mode="gauss")

    elif algorithm == "Mezzotint beta":
        processed_image = mezzo(image, settings, mode="beta")

    elif algorithm == "Bayer":
        processed_image = bayer(image, settings)

    elif algorithm == "Floyd-Steinberg":
        kernel = np.array([[0, 0, 0], [0, 0, 7], [3, 5, 1]], dtype=np.float64) / 16.0

        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "False Floyd-Steinberg":
        kernel = np.array([[0, 0, 0], [0, 0, 3], [0, 3, 2]], dtype=np.float64) / 8.0

        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Jarvis":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 7, 5],
                    [3, 5, 7, 5, 3],
                    [1, 3, 5, 3, 1],
                ],
                dtype=np.float64,
            )
            / 48.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Stucki":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 8, 4],
                    [2, 4, 8, 4, 2],
                    [1, 2, 4, 2, 1],
                ],
                dtype=np.float64,
            )
            / 42.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Stucki small":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 8, 2],
                    [0, 2, 8, 2, 0],
                    [0, 0, 2, 0, 0],
                ],
                dtype=np.float64,
            )
            / 24.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Stucki large":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 8, 4, 2],
                    [2, 4, 8, 8, 8, 4, 2],
                    [2, 4, 4, 4, 4, 4, 2],
                    [2, 2, 2, 2, 2, 2, 2],
                ],
                dtype=np.float64,
            )
            / 88.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Atkinson":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 1],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                ],
                dtype=np.float64,
            )
            / 8
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Burkes":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 8, 4],
                    [2, 4, 8, 4, 2],
                    [0, 0, 0, 0, 0],
                ],
                dtype=np.float64,
            )
            / 32.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Sierra":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 5, 3],
                    [2, 4, 5, 4, 2],
                    [0, 2, 3, 2, 0],
                ],
                dtype=np.float64,
            )
            / 32.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Sierra2":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 4, 3],
                    [1, 2, 3, 2, 1],
                    [0, 0, 0, 0, 0],
                ],
                dtype=np.float64,
            )
            / 16.0
        )
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Sierra2 4A":
        kernel = np.array([[0, 0, 0], [0, 0, 2], [1, 1, 0]], dtype=np.float64) / 4.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Nakano":
        kernel = np.array(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 6, 4],
                [0, 1, 6, 0, 0, 5, 3],
                [0, 0, 4, 7, 3, 5, 3],
                [0, 0, 3, 5, 3, 4, 2],
            ],
            dtype=np.float64,
        )
        kernel /= float(np.sum(kernel))  # Normalize the kernel
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "None":
        # No processing, return the original image
        processed_image = image

    else:
        # Default case: No processing applied if algorithm is unknown
        print(f"Algorithm {algorithm} not recognized, no processing applied.")
        processed_image = image

    return processed_image


class ImageProcessor(QObject):
    """
    This class processes images using various halftoning algorithms in a separate thread.
    It emits progress updates and processed images back to the main thread.

    Attributes:
        result_signal: Signal to send the processed image to the main thread.
        algorithm: The halftoning algorithm to apply.
        settings: Settings for the algorithm, such as error diffusion parameters.
        storage: The ImageStorage instance to access the image data.
    """

    result_signal = Signal(bool)

    # The ProcessPoolExecutor for all worker processes
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)

    def __init__(self, main_window, storage, parent=None):
        """
        Initialize the ImageProcessor with the selected algorithm, settings, and storage instance.

        :param algorithm: The halftoning algorithm to apply.
        :param settings: The settings for the algorithm.
        :param storage: The ImageStorage instance for accessing image data.
        """
        super().__init__(parent)

        self.processing = False
        self.queued_call = None

        self.storage = storage
        self.main_window = main_window
        self.algorithm = "None"
        self.grayscale_mode = "Luminance"  # Initialize the processor with Luminance as the grayscale mode as it is the best.
        self.grayscale_settings = {}

        self.image_settings = {
            "normalize": False,
            "equalize": False,
            "bc_t": False,
            "blur_t": False,
            "unsharp_t": False,
            "brightness": 0.0,
            "contrast": 0.0,
            "sharpness": 0.0,
            "blur": 0.0,
        }

        self.settings = {}

        self.convert = True  # Does the image need reconversion from RGB to Grayscale
        self.reset = True  # Does the viewer need to be reset. Set to True when a new image is loaded.

    @queue
    def start(self, step=0):
        """Start the image processing in a separate process."""

        if self.storage.original_image is None:
            return

        # Displays the Processing... label in the viewer
        self.main_window.viewer.labelVisible(True)

        # The conversion step should only happen if the original image is not actually grayscale, and the grayscale mode has changed when start() was called.
        convert = not self.storage.original_grayscale and step == 0
        enhance = step <= 1

        if convert:
            original_image = self.storage.get_original_image()
            future = self.executor.submit(
                worker_g,
                original_image,
                self.grayscale_mode,
                self.grayscale_settings,
            )

            grayscale_image = future.result()
            self.storage.grayscale_image = grayscale_image

        if enhance:
            grayscale_image = self.storage.get_grayscale_image()
            future = self.executor.submit(
                worker_e,
                grayscale_image,
                self.image_settings,
            )
            enhanced_image = future.result()
            self.storage.enhanced_image = enhanced_image

        enhanced_image = self.storage.get_enhanced_image()
        future = self.executor.submit(
            worker_h,
            enhanced_image,
            self.algorithm,
            self.settings,
        )
        processed_image = future.result()

        try:
            self.send_result(processed_image)
        except Exception as e:
            print(e)

    def wait_for_result(self, future):
        while not future.done():
            QCoreApplication.processEvents()

    def send_result(self, image):
        self.storage.set_processed_image(image, self.reset)

        # Go back to default behavior
        if self.reset:
            self.reset = False

    def _delayed_method_call(self, method, args, kwargs):
        method(self, *args, **kwargs)

    def handle_error(self, error_message):
        """Handle any errors during processing."""
        print(f"Error during processing: {error_message}")
