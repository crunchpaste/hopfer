from PySide6.QtCore import QCoreApplication, QObject, Signal
import numpy as np
from multiprocessing import Process, Queue
import time
from PIL import Image, ImageFilter, ImageEnhance

from helpers.image_conversion import numpy_to_pixmap, pixmap_to_numpy
from helpers.debounce import debounce
try:
    from algorithms.thresholdc import threshold, sauvola_threshold, phansalkar_threshold
except ImportError:
    from algorithms.threshold import threshold, sauvola_threshold, phansalkar_threshold

try:
    from algorithms.mezzoc import mezzo
except ImportError:
    from algorithms.mezzo import mezzo

try:
    from algorithms.error_diffusionc import error_diffusion
except ImportError:
    from algorithms.error_diffusion import error_diffusion

try:
    from algorithms.static import luminance, luma, average, value, lightness
except ImportError:
    from algorithms.grayscale import luminance, luma, average, value, lightness

try:
    from algorithms.static import sharpen
except ImportError:
    from algorithms.sharpen import sharpen

def worker_g(queue, image, mode):
    """
    This is the worker for grayscale conversion. Currently it is just being terminated not quite gracefully, though it seems to not be a problem. This is the only way I've found for the GUI to not freeze while processing.
    """
    print("CONVERTING")
    image = convert_to_grayscale(image, mode)
    queue.put(image)
    return

def worker_e(queue, image, im_settings):
    """
    This is the worker for image enchancements e.g. blurs. As with worker_g and worker_h it is just being terminated.
    """
    print("ENHANCING")
    _brightness = im_settings["brightness"] / 100
    if _brightness > 0:
        # using a log function makes the adjustment feel a bit more natural
        _brightness = 5 * (np.log(1 + (.01 - 1) * _brightness) / np.log(.01))
        print('Bright: ', _brightness)
    _brightness += 1
    _contrast = (im_settings["contrast"] / 100)
    if _contrast > 0:
        # using a log function makes the adjustment feel a bit more natural
        _contrast = 5 * (np.log(1 + (.01 - 1) * _contrast) / np.log(.01))
        print('Contrast: ', _contrast)
    _contrast += 1
    _blur = im_settings["blur"] / 10
    _sharpness = im_settings["sharpness"]

    pil_needed = False
    converted = False # if the image has already been converted back

    if _contrast != 1.0 or \
       _brightness != 1.0 or \
       _blur > 0:

       # if PIL manupulation is needed, convert to a PIL image once
       pil_needed = True

       _image = (image * 255).astype(np.uint8)
       pil_image = Image.fromarray(_image)

    if _brightness != 1.0:
        # if PIL manupulation is needed, convert to a PIL image once
        pil_needed = True
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(_brightness)
    if _contrast != 1.0:
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(_contrast)
    if _blur > 0:
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(_blur))
    if _sharpness > 0:
        converted = True
        if pil_needed:
            _image = np.array(pil_image) / 255
        else:
            _image = image
        image = sharpen(_image, _sharpness)

    if not converted and pil_needed:
        # this will get the image back to a numpy array if it is not done already by the sharpness filter. should be removed when unsharp is implemented.
        image = np.array(pil_image) / 255

    queue.put(image)
    return

def worker_h(queue, image, algorithm, settings):
    """
    This is the worker for halftoning. As with worker_g and worker_e it is just being terminated.
    """
    print("PROCESSING")
    processed_image = apply_algorithm(image, algorithm, settings)
    queue.put(processed_image)
    return

def convert_to_grayscale(image, mode):
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
    else:
        return luminance(image)

def apply_algorithm(image, algorithm, settings):
    """
    Apply the selected halftoning algorithm to the image via worker_p.

    :param image: The original image as a NumPy array.
    :param settings: Settings for the algorithm (like threshold, dither levels).
    :return: The processed image as a NumPy array.
    """
    print(f"Applying {algorithm} to the image with settings: {settings}")

    # Apply the chosen halftoning algorithm using the respective kernel
    if algorithm == "Threshold":
        processed_image = threshold(image, settings)

    elif algorithm == "Sauvola threshold":
        processed_image = sauvola_threshold(image, settings)

    elif algorithm == "Phansalkar threshold":
        processed_image = phansalkar_threshold(image, settings)

    elif algorithm == "Mezzo":
        processed_image = mezzo(image, settings)

    elif algorithm == "Floyd-Steinberg":
        kernel = np.array([[0, 0, 0],
                           [0, 0, 7],
                           [3, 5, 1]], dtype=float) / 16.0
        processed_image = error_diffusion(image,
                                          kernel,
                                          settings)

    elif algorithm == "False Floyd-Steinberg":
        kernel = np.array([[0, 0, 0],
                           [0, 0, 3],
                           [0, 3, 2]], dtype=float) / 8.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Jarvis":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 7, 5],
                           [3, 5, 7, 5, 3],
                           [1, 3, 5, 3, 1]], dtype=float) / 48.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Stucki":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 8, 4],
                           [2, 4, 8, 4, 2],
                           [1, 2, 4, 2, 1]], dtype=float) / 42.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Stucki Small":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 8, 2],
                           [0, 2, 8, 2, 0],
                           [0, 0, 2, 0, 0]], dtype=float) / 24.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Stucki Large":
        kernel = np.array([[0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 8, 4, 2],
                           [2, 4, 8, 8, 8, 4, 2],
                           [2, 4, 4, 4, 4, 4, 2],
                           [2, 2, 2, 2, 2, 2, 2]], dtype=float) / 88.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Atkinson":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 1, 1],
                           [0, 1, 1, 1, 0],
                           [0, 0, 1, 0, 0]], dtype=float) / 8
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Burkes":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 8, 4],
                           [2, 4, 8, 4, 2],
                           [0, 0, 0, 0, 0]], dtype=float) / 32.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Sierra":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 5, 3],
                           [2, 4, 5, 4, 2],
                           [0, 2, 3, 2, 0]], dtype=float) / 32.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Sierra2":
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 4, 3],
                           [1, 2, 3, 2, 1],
                           [0, 0, 0, 0, 0]], dtype=float) / 16.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Sierra2 4A":
        kernel = np.array([[0, 0, 0],
                           [0, 0, 2],
                           [1, 1, 0]], dtype=float) / 4.0
        processed_image = error_diffusion(image, kernel, settings)

    elif algorithm == "Nakano":
        kernel = np.array([[0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 6, 4],
                           [0, 1, 6, 0, 0, 5, 3],
                           [0, 0, 4, 7, 3, 5, 3],
                           [0, 0, 3, 5, 3, 4, 2]], dtype=float)
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
        progress_signal: Signal to update progress in the main thread.
        result_signal: Signal to send the processed image to the main thread.
        algorithm: The halftoning algorithm to apply.
        settings: Settings for the algorithm, such as error diffusion parameters.
        storage: The ImageStorage instance to access the image data.
    """

    progress_signal = Signal(int)
    result_signal = Signal(bool)

    def __init__(self, main_window, storage, parent=None):
        """
        Initialize the ImageProcessor with the selected algorithm, settings, and storage instance.

        :param algorithm: The halftoning algorithm to apply.
        :param settings: The settings for the algorithm.
        :param storage: The ImageStorage instance for accessing image data.
        """
        super().__init__(parent)
        self.queue = Queue()
        self.storage = storage
        self.main_window = main_window
        self.algorithm = "None"
        self.grayscale_mode = "Luminance" # Initialize the processor with Luminance as the grayscale mode as it is the best.
        self.settings = {}

        self.image_settings = {
        "brightness": 0.0,
        "contrast": 0.0,
        "sharpness": 0.0,
        "blur": 0.0
        }

        self.convert = True # Does the image need reconversion from RGB to Grayscale
        self.reset = True # Does the viewer need to be reset. Set to True when a new image is loaded.

    @debounce(0.5)
    def start(self, step=0):
        """Start the image processing in a separate process."""
        if self.storage.original_image is None:
            return

        # Displays the Processing... label in the viewer
        self.main_window.viewer.labelVisible(True)

        # Checks if there is another process running already. If there is terminates it.
        try:
            if self.process.is_alive():
                self.process.terminate()
                self.pocess.join()
        except:
            pass

        # The conversion step should only happen if the original image is not actually grayscale, and the grayscale mode has changed when start() was called.
        convert = (not self.storage.original_grayscale and step == 0)

        if convert:
            image = self.storage.get_original_image()
            mode = self.grayscale_mode
            self.queue = Queue()
            self.process = Process(target=worker_g, args=(self.queue,
                                                          image,
                                                          mode))

            self.process.start()
            grayscale_img = self.wait_for_process()
            self.process.join()

            # Set the result as the new grayscale image to avoid reprocessing it again.
            self.storage.grayscale_image = grayscale_img
        else:
            grayscale_img = self.storage.get_grayscale_image()

        enchance = step <= 1

        if enchance:
            image = self.storage.get_grayscale_image()
            im_settings = self.image_settings
            self.queue = Queue()
            self.process = Process(target=worker_e, args=(self.queue,
                                                         image,
                                                         im_settings))
            self.process.start()
            enhanced_image = self.wait_for_process()
            self.process.join()

            # Set the result as the storage enhanced image to avoid furher reprocessing.
            self.storage.enhanced_image = enhanced_image




        image = self.storage.get_enhanced_image()
        algorithm = self.algorithm
        settings = self.settings
        self.queue = Queue()

        # Creates the subprocess
        self.process = Process(target=worker_h, args=(self.queue,
                                                      image,
                                                      algorithm,
                                                      settings))
        # Actually start the process
        self.process.start()

        # Tries to get the resulting image in a while. If it is not yet available the GUI is repainted.
        processed_image = self.wait_for_process()

        try:
            self.send_result(processed_image)
            self.process.join()
        except:
            pass

    def wait_for_process(self):
        while self.process.is_alive():
            try:
                _image = self.queue.get_nowait()
                return _image
            except:
                QCoreApplication.processEvents()

    def send_result(self, image):
        self.storage.set_processed_image(image, self.reset)

        # Go back to default behavior
        if self.reset:
            self.reset = False

    def handle_error(self, error_message):
        """Handle any errors during processing."""
        print(f"Error during processing: {error_message}")
