import logging
import os
import pickle
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from urllib.parse import unquote, urlparse

import cv2
import numpy as np
import requests
from platformdirs import user_pictures_dir
from PySide6.QtGui import QPixmap

from hopfer.helpers.image_conversion import numpy_to_pixmap

try:
    from hopfer.core.algorithms.cython_ops import style_alpha, style_image
except ImportError:
    from hopfer.core.algorithms.numba_ops import style_alpha, style_image

logger = logging.getLogger(__name__)


class ImageStorage:
    """
    Class for managing the loading, processing, and saving of images.
    Handles the original and processed image, as well as varous conversions.
    """

    MAX_SAVE_ATTEMPTS = 100

    def __init__(self, daemon):
        """
        Initialize the image storage.

        :param daemon: The daemon, used to get the shared environment - the processor, the queue, the paths.
        """
        super().__init__()

        self.daemon = daemon

        self.res_queue = self.daemon.res_queue
        self.req_queue = self.daemon.req_queue

        self.shm = None
        self.shm_preview = None

        self.save_path_edited = False  # Track if the save path has been altered

        self.save_like_preview = False
        self.save_like_alpha = False

        self.original_image = None  # uint16
        self.original_grayscale = False
        self.resized = None  # uint16
        # self.grayscale_image = None  # uint16
        self.enhanced_image = None  # uint16
        self.alpha = None  # uint8
        self.ignore_alpha = False
        self.edited_image = None
        self.processed_image = None  # bool

        self.color_dark = np.array((28, 27, 31)).astype(np.uint8)
        self.color_light = np.array((255, 255, 255)).astype(np.uint8)
        self.color_alpha = np.array((250, 128, 114)).astype(np.uint8)

        self.reset_view = True
        self.algorithm = "None"

    def create_shm(self, height, width):
        if self.shm is not None:
            self.shm.close()
            message = {
                "type": "close_shm",
            }
            self.res_queue.put(message)

            self.shm.unlink()
        self.shm = SharedMemory(
            size=height * width * 3, create=True, track=False
        )
        self.shm_preview = np.ndarray(
            (height, width, 3), dtype=np.uint8, buffer=self.shm.buf
        )
        message = {
            "type": "shared_array",
            "name": self.shm.name,
            "size": (height, width, 3),
        }
        self.res_queue.put(message)

    def reset(self):
        # keeps the paths but discards all images
        # mostly there to make it easier to take screencaptures
        self._original_image = None
        self.resized = None
        self.original_grayscale = False
        self._grayscale_image = None
        self.enhanced_image = None
        self.alpha = None
        self.ignore_alpha = False
        self.edited_image = None
        self.processed_image = None

        self.reset_view = True

        message = {
            "type": "has_image",
            "value": False,
        }

        self.res_queue.put(message)

    def _load(self, image):
        # the final procedure of loading an image. expecs a numpy array.

        self.original_image, self.alpha = self.extract_alpha(image)
        self.resized = self.original_image.copy()
        h, w = self.original_image.shape[0], self.original_image.shape[1]

        # shared memory seems to be a mess on windows, therefore just avoiding
        # it by serializing the arrays and sending them over a queue. its slow,
        # its ugly, but it is what it is.
        message = {
            "type": "has_image",
            "value": True,
        }

        self.res_queue.put(message)

        try:
            self.create_shm(h, w)
        except Exception as e:
            logger.error(f"Failed creating SHM: {e}")

        message = {
            "type": "original_grayscale",
            "value": self.original_grayscale,
        }

        self.res_queue.put(message)

        if self.original_grayscale:
            self.grayscale_image = None
        else:
            self.grayscale_image = None

        self.enhanced_image = None
        self.processed_image = None
        self.daemon.processor.reset = True

        try:
            logger.debug("Started processing")
            self.daemon.processor.start(step=0)
        except Exception as e:
            logger.warning(f"Failed processing: {e}")

    def load_image(self, image_path):
        """
        Load an image from a given path and convert it to grayscale (L mode).

        :param image_path: Path to the image file to load.
        """

        cv_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if cv_image is None:
            file_bytes = np.fromfile(image_path, dtype=np.uint8)
            cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

        if cv_image is not None:
            self._load(cv_image)
        else:
            self.show_notification("Unsupported image format", duration=7000)
            self.load_failed()

    def load_from_pickle(self, data):
        buffer = pickle.loads(data)
        if not isinstance(buffer, np.ndarray):
            image = np.array(buffer)
        else:
            image = buffer
        logger.debug(f"Loaded from pickle. dtype: {image.dtype} ")
        self._load(image)

    def load_from_url(self, url, local):
        if url != "":
            if local:
                parsed_url = urlparse(url)
                local_path = unquote(parsed_url.path)
                if os.name == "nt":
                    local_path = local_path.lstrip("/")
                url = local_path
                self.load_image(url)
            else:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = np.frombuffer(response.content, np.uint8)
                    cv_image = cv2.imdecode(image_data, cv2.IMREAD_UNCHANGED)
                    self._load(cv_image)

                else:
                    self.show_notification(
                        f"{response.status_code}: Failed to download image",
                        duration=10000,
                    )
                    self.load_failed()
                    return None
        else:
            self.show_notification("No image data in clipboard", duration=10000)
            self.load_failed()

    def load_failed(self):
        message = {"type": "load_failed"}
        self.res_queue.put(message)

    @staticmethod
    def discard_alpha(alpha):
        # discard the alpha channel if its full of equal numbers
        # to save on furher processing.
        if np.all(alpha == alpha[0, 0]):
            return None
        else:
            return alpha

    def extract_alpha(self, image):
        """
        Extracts alpha and color/grayscale channels from an OpenCV image based on its channels.
        Assumes image was loaded with cv2.IMREAD_UNCHANGED.
        """

        np_image_uint16 = self.image_to_uint16(image)
        if len(np_image_uint16.shape) == 2:
            num_channels = 1
        else:
            num_channels = np_image_uint16.shape[-1]

        h, w = np_image_uint16.shape[0], np_image_uint16.shape[1]

        self.res_queue.put(
            {"type": "image_size", "height": h, "width": w, "ratio": h / w},
            block=False,
        )
        if num_channels == 1:
            logger.debug("Image has 1 channel")
            L = np_image_uint16
            A = None
            self.original_grayscale = True
            return L, A

        elif num_channels == 2:
            # This one is never used as cv2 converts them automatically to RGBA
            logger.debug("Image has 2 channels")
            L = np_image_uint16[:, :, 0]
            A = (self.discard_alpha(np_image_uint16[:, :, 1]) >> 8).astype(
                np.uint8
            )

            cv2.imwrite("test_alpha.png", A)
            logger.debug("Saved alpha as an image")

            self.original_grayscale = True
            return L, A

        elif num_channels == 3:
            logger.debug("Image has 3 channels")
            BGR = np_image_uint16
            RGB = self.bgr_to_rgb(BGR)
            A = None

            # Check for grayscale conversion and status update
            RGB, is_gray = self.check_grayscale(RGB)

            self.original_grayscale = is_gray
            return RGB, A  # Color_BGR is (H, W, 3), A is None

        elif num_channels == 4:
            logger.debug("Image has 4 channels")
            BGR = np_image_uint16[:, :, :3]
            RGB = self.bgr_to_rgb(BGR)
            # TODO: Fix the logic here so that the alpha is 16bit if needed

            alpha_tmp = self.discard_alpha(np_image_uint16[:, :, 3])

            if alpha_tmp is not None:
                if alpha_tmp.dtype == np.uint16:
                    A = (alpha_tmp >> 8).astype(np.uint8)
                else:
                    A = alpha_tmp
            else:
                A = None

            # Check for grayscale conversion and status update
            RGB, is_gray = self.check_grayscale(RGB)

            self.original_grayscale = is_gray
            return RGB, A

        else:
            self.show_notification("Unsupported number of channels")

    @staticmethod
    def bgr_to_rgb(image):
        RGB = image[:, :, ::-1]
        return RGB

    @staticmethod
    def image_to_uint16(image):
        image_dtype = image.dtype
        logger.debug(f"Image arrived at storage as {image_dtype}")
        # if image_dtype == np.uint8:
        #     image = image.astype(np.uint16)e << 8

        return image

    @staticmethod
    def check_grayscale(rgb):
        """This is just a small function to check if an RGB image is actually grayscale. It saves time and resources on converting it to grayscale later on. Turns out using numpy's array_equal is much faster."""

        if np.array_equal(rgb[:, :, 0], rgb[:, :, 1]) and np.array_equal(
            rgb[:, :, 0], rgb[:, :, 2]
        ):
            r = np.copy(rgb[:, :, 0])
            return r, True
        else:
            return rgb, False

    def resize_original(self, w, h, interpolation):
        resized = self.original_image.copy()

        if interpolation.lower() == "nearest neighbor":
            method = cv2.INTER_NEAREST
        elif interpolation.lower() == "bilinear":
            method = cv2.INTER_LINEAR
        elif interpolation.lower() == "bicubic":
            method = cv2.INTER_CUBIC
        elif interpolation.lower() == "lanczos":
            method = cv2.INTER_LANCZOS4
        else:
            # fallback default
            method = cv2.INTER_LINEAR

        self.resized = cv2.resize(resized, (w, h), interpolation=method)

        try:
            self.create_shm(h, w)
        except Exception as e:
            logger.error(f"Failed creating SHM: {e}")

        if self.original_grayscale:
            self.grayscale_image = None

        try:
            self.daemon.processor.reset = True
            self.daemon.processor.start(step=0)
        except Exception as e:
            logger.error(f"Failed processing: {e}")

    def save_image(self, path):
        """
        Save the processed image to the disk. If the file already exists,
        it appends a counter to the filename to avoid overwriting.

        If the image is processed, save it, else, do nothing.
        """
        if self.processed_image is None:
            self.show_notification(
                "No image is loaded",
                duration=3000,
            )
            return

        save_path = path

        if not save_path:
            base_path = user_pictures_dir()
            save_path = os.path.join(base_path, "hopfer.png")

        base_path = os.path.dirname(save_path)
        base_name = os.path.basename(save_path)
        save_path = self.generate_unique_save_path(base_path, base_name)

        if self.save_like_preview and self.daemon.processor.algorithm != "None":
            image = style_image(
                self.processed_image, self.color_dark, self.color_light
            )
        else:
            image = self.processed_image.astype(np.uint8)

        if self.ignore_alpha or self.alpha is None:
            output_image = image
        else:
            alpha = self.alpha
            output_image = np.dstack((image, alpha))

        # this part handles the RGB to BGR conversion needed for cv2.
        if output_image.ndim == 3:
            num_channels = output_image.shape[-1]

            # HACK: cv2 can't handle grayscale with alpha so this is needed
            if num_channels == 2:
                gray = output_image[:, :, 0]
                alpha = output_image[:, :, 1]

                # Convert grayscale → BGR
                bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

                # Rebuild BGRA
                output_image = np.dstack((bgr, alpha))

            if num_channels == 3:
                output_image = output_image[:, :, ::-1]

            elif num_channels == 4:
                # RGBA -> BGRA conversion
                output_image = output_image[:, :, [2, 1, 0, 3]]

        try:
            success = cv2.imwrite(save_path, output_image)
            if not success:
                # HACK: used numpy to bypass windows problems with non-latin encoding of folder and file names
                ext = os.path.splitext(save_path)[1]
                np_success, buffer = cv2.imencode(ext, output_image)

                if np_success:
                    buffer.tofile(save_path)

        except Exception as e:
            self.show_notification(f"Error: {e}", duration=10000)
            return

        filename = os.path.basename(save_path)

        folder = os.path.basename(os.path.dirname(save_path))

        friendly_path = f".../{folder}/{filename}"

        folder_path = os.path.dirname(save_path)

        # check if the file actually exists on disk. i've had some problems with false positives before, so better safe than sorry.
        if os.path.exists(save_path):
            folder_uri = Path(folder_path).as_uri()
            # safe_uri = urllib.parse.quote(folder_uri, safe=':/')

            message = (
                f"Saved to <a href='{folder_uri}'><b>{friendly_path}</b></a>"
            )
            self.show_notification(message, duration=5000)
        else:
            message = "Failed to save image"
            self.show_notification(message, duration=5000)

    def save_to_clipboard(self):
        if self.processed_image is not None:
            styled = self.save_like_preview

            # TODO: I have to check how to create pixmaps directly from an array
            img = self.generate_processed_pixmap(
                compositing=False, styled=styled, clipboard=True
            )
            pickled_image = pickle.dumps(img)
            message = {"type": "data_for_clipboard", "data": pickled_image}
            self.res_queue.put(message)
            self.show_notification("Image stored in clipboard")
        else:
            self.show_notification("No image is loaded", duration=5000)

    def generate_unique_save_path(self, base_path, base_name):
        """
        Generate a unique save path for the image. If the file exists,
        a counter is appended to the base filename.
        """
        # Extract the file extension (format) from the base_name
        base_name_without_ext = base_name.rsplit(".", 1)[0]
        file_format = (
            "." + base_name.rsplit(".", 1)[1] if "." in base_name else ".png"
        )

        counter = 1
        save_path = os.path.join(
            base_path, f"{base_name_without_ext}{file_format}"
        )

        while os.path.exists(save_path) and counter < self.MAX_SAVE_ATTEMPTS:
            save_path = os.path.join(
                base_path, f"{base_name_without_ext}_{counter:03d}{file_format}"
            )
            counter += 1

        return save_path

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

    def generate_processed_pixmap(
        self, compositing=True, styled=True, clipboard=False
    ):
        reset = self.reset_view
        processor = self.daemon.processor

        if self.original_image is not None:
            if processor.algorithm == "None":
                return self._handle_no_algorithm(reset, clipboard)

            result = self._process_image(compositing, styled)
            if clipboard:
                return result

            self.shm_preview[:] = result
            self.res_queue.put(
                {"type": "display_image", "array": "rgb", "reset": reset}
            )
            logger.debug("Sent image to bridge")

            processor.processing = False

    def _handle_no_algorithm(self, reset, clipboard):
        # Handles the case when "None" is the algo
        try:
            processed_img = np.ascontiguousarray(self.processed_image)
            logger.debug(f"Processed: {processed_img.dtype}")
            if not clipboard:
                self.shm_preview[:, :, 0] = processed_img
                self.res_queue.put(
                    {
                        "type": "display_image",
                        "array": "gray",
                        "reset": reset,
                    }
                )
        except Exception as e:
            logger.error(f"Failed generating pixmaps: {e}")

        return processed_img if clipboard else None

    def _process_image(self, compositing, styled):
        # Applies styling
        if not styled:
            return self._convert_to_uint8()

        color_params = (self.color_dark, self.color_light, self.color_alpha)

        if self.alpha is not None:
            return self._apply_styling_with_alpha(compositing, *color_params)

        return style_image(self.processed_image, *color_params[:2])

    def _apply_styling_with_alpha(
        self, compositing, color_dark, color_light, color_alpha
    ):
        logger.debug(
            f"Alpha styling image of dtype: {self.processed_image.dtype}"
        )
        logger.debug(f"Alpha channel of dtype: {self.alpha.dtype}")
        # Applies the styling and composits
        if compositing:
            try:
                return style_alpha(
                    self.processed_image,
                    self.alpha,
                    color_dark,
                    color_light,
                    color_alpha,
                )
            except Exception as e:
                logger.error(f"Failed compositing {e}")

        styled_img = style_image(self.processed_image, color_dark, color_light)
        alpha = self.alpha
        return np.dstack((styled_img, alpha))

    def _convert_to_uint8(self):
        # Cenverts to uint8 and adds alpha
        img_uint8 = self.processed_image.astype(np.uint8) * 255

        if self.alpha is not None:
            alpha = self.alpha
            return np.dstack((img_uint8, img_uint8, img_uint8, alpha))

        return img_uint8

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

    def set_processed_image(self, processed_image, reset):
        """
        Store the processed image.

        :param processed_image: Processed image as a NumPy array.
        """

        self.processed_image = processed_image

    def rotate_image(self, cw=True):
        if cw:
            self.original_image = np.rot90(self.original_image, k=-1)
            self.resized = np.rot90(self.resized, k=-1)
            self.enhanced_image = np.rot90(self.enhanced_image, k=-1)
            self.processed_image = np.rot90(self.processed_image, k=-1)
            if self.alpha is not None:
                self.alpha = np.rot90(self.alpha, k=-1)
            self.shm_preview = np.rot90(self.shm_preview, k=-1)
        else:
            self.original_image = np.rot90(self.original_image, k=1)
            self.resized = np.rot90(self.resized, k=1)
            self.enhanced_image = np.rot90(self.enhanced_image, k=1)
            self.processed_image = np.rot90(self.processed_image, k=1)
            if self.alpha is not None:
                self.alpha = np.rot90(self.alpha, k=1)
            # if os.name != "nt":
            self.shm_preview = np.rot90(self.shm_preview, k=1)

        h, w = self.resized.shape[:2]
        self.res_queue.put(
            {"type": "image_size", "height": h, "width": w, "ratio": h / w}
        )

        # while this does not produce accurate results for the dithering it is much faster than reprocessing the image on each transform. the halftoning would be accurate again on the next reprocess.
        self.reset_view = True

    def flip_image(self):
        self.original_image = np.fliplr(self.original_image)
        self.resized = np.fliplr(self.resized)
        # self.grayscale_image = np.fliplr(self.grayscale_image)
        self.enhanced_image = np.fliplr(self.enhanced_image)
        self.processed_image = np.fliplr(self.processed_image)
        if self.alpha is not None:
            self.alpha = np.fliplr(self.alpha)

        # while this does not produce accurate results for the dithering it is much faster than reprocessing the image on each transform. the halftoning would be accurate again on the next reprocess.

    def invert_image(self):
        if self.original_image.dtype == np.uint16:
            self.original_image = 65535 - self.original_image
            self.resized = 65535 - self.resized
            self.enhanced_image = 65535 - self.enhanced_image
        else:
            self.original_image = 255 - self.original_image
            self.resized = 255 - self.resized
            self.enhanced_image = 255 - self.enhanced_image

        logger.debug(f"Enhanced image: {self.enhanced_image.dtype}")
        logger.debug(f"Processed image: {self.processed_image.dtype}")
        if self.processed_image.dtype == np.uint8:
            self.processed_image = 255 - self.processed_image
        elif self.processed_image.dtype in [np.bool, np.bool_]:
            np.logical_not(self.processed_image, out=self.processed_image)

        # It may be a bit of a personal preference, but i don't believe
        # the view should be reset after inverting the colors.

    def show_notification(self, notification, duration=3000):
        """
        Show a notification in the main window's sidebar.
        """
        message = {
            "type": "notification",
            "notification": notification,
            "duration": duration,
        }
        self.res_queue.put(message)

    def update_paths(self):
        message = {
            "type": "update_paths",
            "paths": self.paths,
        }
        self.res_queue.put(message)
