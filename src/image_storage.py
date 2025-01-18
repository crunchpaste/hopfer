import os
from PIL import Image, UnidentifiedImageError
import numpy as np
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap
from helpers.image_conversion import numpy_to_pixmap

class ImageStorage:
    """
    Class for managing the loading, processing, and saving of images.
    Handles original and processed images.
    """

    # Constants for image processing and saving
    IMAGE_FORMAT = "png"
    MAX_SAVE_ATTEMPTS = 100
    NORMALIZED_MAX = 255.0

    def __init__(self, main_window):
        """
        Initialize the image storage with the main window context for notifications.

        :param main_window: The main window of the application, used for showing notifications.
        """
        self.main_window = main_window
        self.image_path = None
        self.save_path = None
        self.original_image = None
        self.grayscale_image = None
        self.edited_image = None
        self.processed_image = None
        self.save_path_edited = False  # Track if the save path has been altered

    def load_image(self, image_path):
        """
        Load an image from a given path and convert it to grayscale (L mode).

        :param image_path: Path to the image file to load.
        """
        try:
            self.image_path = image_path
            self.save_path = image_path

            # Open the image and convert to grayscale
            pil_image = Image.open(image_path).convert("RGB")
            self.original_image = np.array(pil_image) / self.NORMALIZED_MAX
            self.main_window.sidebar.toolbox.enable_save()
        except (FileNotFoundError, UnidentifiedImageError) as e:
            self.show_notification(f"Error: Unable to open image.\n{str(e)}", duration=10000)
        except Exception as e:
            self.show_notification(f"An unexpected error occurred: {str(e)}", duration=10000)

    def save_image(self):
        """
        Save the processed image to the disk. If the file already exists,
        it appends a counter to the filename to avoid overwriting.

        If the image is processed, save it, else, do nothing.
        """
        if self.processed_image is None:
            print("No processed image to save!")
            return

        # Ensure the base name and directory are properly set
        if not self.save_path:
            print("No image path specified!")
            return

        base_dir = os.path.dirname(self.save_path)
        base_name = os.path.splitext(os.path.basename(self.save_path))[0]
        save_path = self.generate_unique_save_path(base_dir, base_name)

        # Convert processed image to PIL format and save
        pil_image = Image.fromarray((self.processed_image * 255).astype(np.uint8))
        pil_image.save(save_path)

        self.show_notification(f"Image saved to {save_path}", duration=3000)
        print(f"Image saved to {save_path}")

    def generate_unique_save_path(self, base_dir, base_name):
        """
        Generate a unique save path for the image. If the file exists,
        a counter is appended to the base filename.

        :param base_dir: The directory to save the image.
        :param base_name: The base name of the file (without extension).
        :return: A unique file path for saving.
        """
        counter = 1
        save_path = os.path.join(base_dir, f"{base_name}.{self.IMAGE_FORMAT}")

        while os.path.exists(save_path) and counter < self.MAX_SAVE_ATTEMPTS:
            save_path = os.path.join(base_dir, f"{base_name}_{counter:03d}.{self.IMAGE_FORMAT}")
            counter += 1

        return save_path

    def get_original_image(self):
        """
        Return the original image as a NumPy array (normalized to [0, 1]).

        :return: Original image array.
        """
        return self.original_image

    def get_grayscale_image(self):
        """
        Return the grayscale image as a NumPy array (normalized to [0, 1]).

        :return: Grayscale image array.
        """
        return self.grayscale_image

    def get_original_pixmap(self):
        """
        Convert the original image to a QPixmap.

        :return: QPixmap of the original image.
        """
        return self._get_image_pixmap(self.original_image)

    def get_grayscale_pixmap(self):
        """
        Convert the grayscale image to a QPixmap.

        :return: QPixmap of the grayscale image.
        """
        return self._get_image_pixmap(self.grayscale_image)

    def get_processed_image(self):
        """
        Return the processed image.

        :return: Processed image array.
        """
        return self.processed_image

    def get_processed_pixmap(self):
        """
        Convert the processed image to a QPixmap. If no processed image exists,
        return the original pixmap.

        :return: QPixmap of the processed image (or original if not processed).
        """
        return self._get_image_pixmap(self.processed_image) or self.get_original_pixmap()

    def _get_image_pixmap(self, image_array):
        """
        Helper method to convert an image array to QPixmap.

        :param image_array: Image in NumPy array format.
        :return: QPixmap object corresponding to the image array.
        """
        if image_array is not None:
            return numpy_to_pixmap(image_array)
        else:
            return QPixmap()  # Return an empty pixmap if image is None

    def set_processed_image(self, processed_image):
        """
        Store the processed image.

        :param processed_image: Processed image as a NumPy array.
        """
        print("Processed image set")
        self.processed_image = processed_image

    def show_notification(self, message, duration=3000):
        """
        Show a notification in the main window's sidebar.

        :param message: The message to display.
        :param duration: Duration in milliseconds for how long the notification lasts.
        """
        self.main_window.sidebar.notifications.show_notification(message, duration)
