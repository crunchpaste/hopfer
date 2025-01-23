from PySide6.QtCore import QObject, Signal
import numpy as np

from helpers.image_conversion import numpy_to_pixmap, pixmap_to_numpy
try:
    from algorithms.error_diffusionc import error_diffusion
except ImportError:
    from algorithms.error_diffusion import error_diffusion
try:
    from algorithms.static import luminance, luma, average, value, lightness
except ImportError:
    from algorithms.grayscale import luminance, luma, average, value, lightness

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

    def __init__(self, algorithm, settings, storage, parent=None):
        """
        Initialize the ImageProcessor with the selected algorithm, settings, and storage instance.

        :param algorithm: The halftoning algorithm to apply.
        :param settings: The settings for the algorithm.
        :param storage: The ImageStorage instance for accessing image data.
        """
        super().__init__(parent)
        self.storage = storage
        self.algorithm = algorithm
        self.grayscale_mode = "Luminance" # Initialize the processor with Luminance as the grayscale mode as it is the best.
        self.settings = settings
        self.convert = True # Does the image need reconversion from RGB to Grayscale
        self.reset = True # Does the viewer need to be reset. Set to True when a new image is loaded.

    def start(self):
        """ The run method is executed in the separate thread to process the image. """
        try:
            if self.convert:
                original = np.copy(self.storage.get_original_image())
                grayscale = self.convert_to_grayscale(original)
                self.convert = False
                self.storage.grayscale_image = grayscale
                print("Luminance!")
            # Get the original image from storage
            original = np.copy(self.storage.get_grayscale_image())
            # Apply the selected algorithm to the image
            processed_image = self.apply_algorithm(original, self.settings)
            # Store the processed image in the storage
            self.storage.set_processed_image(processed_image)
            # Emit the processed image back to the main thread
            self.result_signal.emit(self.reset)
            self.reset = False
        except Exception as e:
            # Handle errors if any occur during processing
            print(f"Error during processing: {e}")
            self.result_signal.emit(self.reset)  # Emit None if processing fails
            self.reset = False

    def convert_to_grayscale(self, image):

        if self.grayscale_mode == "Luminance":
            return luminance(image)
        if self.grayscale_mode == "Luma":
            return luma(image)
        elif self.grayscale_mode == "Average":
            return average(image)
        elif self.grayscale_mode == "Value":
            return value(image)
        elif self.grayscale_mode == "Lightness":
            return lightness(image)
        else:
            return luminance(image)

    def apply_algorithm(self, image, settings):
        """
        Apply the selected halftoning algorithm to the image.

        :param image: The original image as a NumPy array.
        :param settings: Settings for the algorithm (like threshold, dither levels).
        :return: The processed image as a NumPy array.
        """
        print(f"Applying {self.algorithm} to the image with settings: {settings}")

        # Apply the chosen halftoning algorithm using the respective kernel
        if self.algorithm == "Floyd-Steinberg":
            kernel = np.array([[0, 0, 0],
                               [0, 0, 7],
                               [3, 5, 1]], dtype=float) / 16.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "False Floyd-Steinberg":
            kernel = np.array([[0, 0, 0],
                               [0, 0, 3],
                               [0, 3, 2]], dtype=float) / 8.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Jarvis":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 7, 5],
                               [3, 5, 7, 5, 3],
                               [1, 3, 5, 3, 1]], dtype=float) / 48.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Stucki":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 8, 4],
                               [2, 4, 8, 4, 2],
                               [1, 2, 4, 2, 1]], dtype=float) / 42.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Stucki Small":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 8, 2],
                               [0, 2, 8, 2, 0],
                               [0, 0, 2, 0, 0]], dtype=float) / 24.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Stucki Large":
            kernel = np.array([[0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 8, 4, 2],
                               [2, 4, 8, 8, 8, 4, 2],
                               [2, 4, 4, 4, 4, 4, 2],
                               [2, 2, 2, 2, 2, 2, 2]], dtype=float) / 88.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Atkinson":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 1, 1],
                               [0, 1, 1, 1, 0],
                               [0, 0, 1, 0, 0]], dtype=float) / 8
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Burkes":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 8, 4],
                               [2, 4, 8, 4, 2],
                               [0, 0, 0, 0, 0]], dtype=float) / 32.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Sierra":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 5, 3],
                               [2, 4, 5, 4, 2],
                               [0, 2, 3, 2, 0]], dtype=float) / 32.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Sierra2":
            kernel = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0],
                               [0, 0, 0, 4, 3],
                               [1, 2, 3, 2, 1],
                               [0, 0, 0, 0, 0]], dtype=float) / 16.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Sierra2 4A":
            kernel = np.array([[0, 0, 0],
                               [0, 0, 2],
                               [1, 1, 0]], dtype=float) / 4.0
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "Nakano":
            kernel = np.array([[0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 6, 4],
                               [0, 1, 6, 0, 0, 5, 3],
                               [0, 0, 4, 7, 3, 5, 3],
                               [0, 0, 3, 5, 3, 4, 2]], dtype=float)
            kernel /= float(np.sum(kernel))  # Normalize the kernel
            processed_image = error_diffusion(image, kernel, settings)

        elif self.algorithm == "None":
            # No processing, return the original image
            processed_image = image

        else:
            # Default case: No processing applied if algorithm is unknown
            print(f"Algorithm {self.algorithm} not recognized, no processing applied.")
            processed_image = image

        return processed_image
