from PySide6.QtCore import QThread, Signal
from helpers.image_conversion import numpy_to_pixmap, pixmap_to_numpy
from algorithms.error_diffusionc import error_diffusion
import numpy as np

class ImageProcessor(QThread):
    progress_signal = Signal(int)
    result_signal = Signal(object)

    def __init__(self, algorithm, settings, storage, parent=None):
        super().__init__(parent)
        self.storage = storage # The storage class
        self.algorithm = algorithm # Current halftoning algorithm
        self.settings = settings  # A dictionary with the settings

    def run(self):
        """ The run method is executed in the separate thread. It performs the processing. """
        try:
            original = np.copy(self.storage.get_original_image())
            processed_image = self.apply_algorithm(original, self.settings)

            self.storage.set_processed_image(processed_image)
            # Emit the processed image back to the main thread
            self.result_signal.emit(processed_image)

        except Exception as e:
            # Handle errors if any occur during processing
            print(f"Error during processing: {e}")
            self.result_signal.emit(None)  # In case of failure, send None as result

    def apply_algorithm(self, image, settings):
        """ Placeholder method where the halftoning algorithm is applied to the image using settings """
        print(f"Applying {self.algorithm} to the image with settings: {settings}")

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

            kernel /= float(np.sum(kernel))

            processed_image = error_diffusion(image, kernel, settings)
        elif self.algorithm == "None":
            processed_image  = image
        else:
            processed_image = image  # Default: No processing

        return processed_image
