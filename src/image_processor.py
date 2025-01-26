from PySide6.QtCore import QCoreApplication, QObject, Signal
import numpy as np
from multiprocessing import Process, Queue

from helpers.image_conversion import numpy_to_pixmap, pixmap_to_numpy
from helpers.debounce import debounce

try:
    from algorithms.thresholdc import threshold
except ImportError:
    from algorithms.threshold import threshold

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

def worker_p(queue, image, convert, mode, algorithm, im_settings, settings):
    """
    The main function of the worker to be executed as a subprocess. Currently it is just being terminated not quite gracefully, though it seems to not be a problem. This is the only way I've found for the GUI to not freeze while processing.
    """

    print('W STARTED')
    if convert:
        print("CONVERTING")
        image = convert_to_grayscale(image, mode)
    if im_settings["sharpness"] > 0:
        image = sharpen(image, im_settings["sharpness"])
    processed_image = apply_algorithm(image, algorithm, settings)
    queue.put(processed_image)
    print('W PROCESSED')
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
        "sharpness": 0.0
        }

        self.convert = True # Does the image need reconversion from RGB to Grayscale
        self.reset = True # Does the viewer need to be reset. Set to True when a new image is loaded.

    @debounce(0.5)
    def start(self):
        """Start the image processing in a separate process."""
        if self.storage.original_image is None:
            return

        # Displays the Processing... label in the viewer
        self.main_window.viewer.labelVisible(True)

        #Checks if there is another process running already. If there is terminates it.
        try:
            if self.process.is_alive():
                self.process.terminate()
                self.pocess.join()
        except:
            pass

        convert = not self.storage.original_grayscale

        print('Conver: ', convert)

        image = self.storage.get_original_image()

        mode = self.grayscale_mode

        algorithm = self.algorithm
        settings = self.settings
        im_settings = self.image_settings

        # Creates the subprocess
        self.process = Process(target=worker_p, args=(self.queue,
                                                      image,
                                                      convert,
                                                      mode,
                                                      algorithm,
                                                      im_settings,
                                                      settings))
        # Actually start the process
        self.process.start()

        # Tries to get the resulting image in a while. If it is not yet available the GUI is repainted.
        while self.process.is_alive():
            try:
                processed_image = self.queue.get_nowait()
                break  # Non-blocking
            except:
                QCoreApplication.processEvents()

        try:
            self.send_result(processed_image)
            self.process.join()
        except:
            pass

    def send_result(self, image):
        self.storage.set_processed_image(image, self.reset)

        # Go back to default behavior
        if self.reset:
            self.reset = False

    def handle_error(self, error_message):
        """Handle any errors during processing."""
        print(f"Error during processing: {error_message}")
