import time

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from PySide6.QtCore import QObject

from helpers.decorators import queue
from helpers.kernels import get_kernel

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
    from algorithms.bayerc import bayer, clustered
except ImportError:
    from algorithms.bayer import bayer, clustered

try:
    from algorithms.error_diffusionc import error_diffusion
except ImportError:
    from algorithms.error_diffusion import error_diffusion

from algorithms.variable_ed import variable_ed

try:
    from algorithms.static import (
        average,
        lightness,
        luma,
        luminance,
        manual,
        value,
    )
except ImportError:
    from algorithms.grayscale import (
        average,
        lightness,
        luma,
        luminance,
        manual,
        value,
    )


class ImageProcessor(QObject):
    """
    This class processes images using various halftoning algorithms and is part of the daemon.
    It takes images from ImageStorage and sends the processed images back to storage which sends them to the GUI.
    """

    def __init__(self, daemon, storage):
        """
        Initialize the ImageProcessor with the daemon and an ImageStorage instance.
        """
        super().__init__()

        self.processing = False
        self.queued_call = None

        # The Daemon instance.
        self.daemon = daemon
        # The ImageStorage instance. Used for getting and storing images.
        self.storage = storage
        # This is the response multiprocessing Queue, used to communicate back to the GUI
        self.res_queue = self.daemon.res_queue
        # Initialize the processor with Luminance as the grayscale mode as it is the the most acurate.
        self.grayscale_mode = "Luminance"
        # Grayscale settings left blank as Luminance does not need any
        self.grayscale_settings = {}
        # Image adjustments settings initialized as all disabled
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
        # Algorithm is initialized to None - just returning the original image
        self.algorithm = "None"
        # These are the halftoning settings. Initialized as empty as none does not need any.
        self.settings = {}
        # Convert is used as a flag to indicate that the image is RGB and needs conversion
        self.convert = True
        # Reset is used a flag for the viewer to be reset. Set to True when a new image is loaded.
        self.reset = True

    @queue
    def start(self, step=0):
        """
        The main method of the processor. It processes the image in a sequential manner
        then stores the result in the ImageStorage instance.
        """
        self.processing = True

        if self.storage.original_image is None:
            self.processing = False
            return

        try:
            self.res_queue.put({"type": "started_processing"})

            # Determine the processing step based on grayscale mode and enhancement settings.
            step = self._determine_processing_step(step)

            start_time = time.perf_counter()

            # Perform processing steps sequentially.
            self._process_grayscale(step)
            self._process_enhancement(step)

            processed_image = self._process_algorithm()

        except Exception as e:
            print(e)
            self._handle_processing_error()
            processed_image = self.storage.processed_image

        print(f"PROCESSING: {time.perf_counter() - start_time:.6f} seconds")

        self._send_result(processed_image)

    # --- Helper Methods ---

    def _determine_processing_step(self, step):
        """Determines whether conversion or enhancement should be performed."""
        convert = not self.storage.original_grayscale and step == 0
        enhance = step <= 1
        return 0 if convert else (1 if enhance else step)

    def _process_grayscale(self, step):
        """Converts the image to grayscale if necessary."""
        if step == 0:
            self.storage.grayscale_image = self._convert_to_grayscale(
                self.storage.original_image,
                self.grayscale_mode,
                self.grayscale_settings,
            )

    def _process_enhancement(self, step):
        """Enhances the image based on the provided settings."""
        im_settings = self.image_settings
        if step <= 1 and any(
            im_settings[key]
            for key in ["normalize", "equalize", "bc_t", "blur_t", "unsharp_t"]
        ):
            self.storage.enhanced_image = self._enhance_image(
                self.storage.grayscale_image, im_settings
            )
        elif step <= 1:
            self.storage.enhanced_image = self.storage.grayscale_image

    def _process_algorithm(self):
        """Applies the processing algorithm if selected."""
        if self.algorithm != "None":
            return self._apply_algorithm(
                self.storage.enhanced_image, self.algorithm, self.settings
            )
        return self.storage.enhanced_image

    def _handle_processing_error(self):
        """Handles exceptions during processing."""
        self.res_queue.put(
            {
                "type": "notification",
                "notification": "Something went wrong while processing. Returning last good processed image.",
                "duration": 7000,
            }
        )

    @staticmethod
    def _convert_to_grayscale(image, mode, settings):
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

    @staticmethod
    def _enhance_image(image, im_settings):
        """
        This is the method for image enchancements e.g. blurs.
        """
        _brightness = im_settings["brightness"] / 100

        if _brightness > 0:
            # using a log function makes the adjustment feel a bit more natural
            _brightness = 5 * (
                np.log(1 + (0.01 - 1) * _brightness) / np.log(0.01)
            )
        _brightness += 1
        _contrast = im_settings["contrast"] / 100
        if _contrast > 0:
            # using a log function makes the adjustment feel a bit more natural
            _contrast = 5 * (np.log(1 + (0.01 - 1) * _contrast) / np.log(0.01))
        _contrast += 1
        # _sharpness = im_settings["sharpness"]

        pil_needed = False
        # if the image has already been converted back
        converted = False

        if im_settings["normalize"]:
            min_val = np.min(image)
            max_val = np.max(image)
            image = (image - min_val) / (max_val - min_val)

        if im_settings["equalize"]:
            hist, bins = np.histogram(image.flatten(), bins=256, range=[0, 1])

            cdf = hist.cumsum()
            cdf_normalized = cdf / cdf[-1]

            image = np.interp(
                image.flatten(), bins[:-1], cdf_normalized
            ).reshape(image.shape)

        if (
            im_settings["bc_t"]
            or im_settings["blur_t"]
            or im_settings["unsharp_t"] > 0
        ):
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

            pil_image = pil_image.filter(
                ImageFilter.UnsharpMask(radius, strenght, thresh)
            )

        if not converted and pil_needed:
            # this will get the image back to a numpy array if it is not done already by the sharpness filter. should be removed when unsharp is implemented.
            image = (np.array(pil_image) / 255).astype(np.float32)
        return image

    @staticmethod
    def _apply_algorithm(image, algorithm, settings):
        """Apply the selected halftoning algorithm to the image via worker_h."""

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

        elif algorithm == "Clustered dot":
            processed_image = clustered(image, settings)

        elif algorithm == "Bayer":
            processed_image = bayer(image, settings)

        elif algorithm in [
            "Floyd-Steinberg",
            "False Floyd-Steinberg",
            "Jarvis",
            "Stucki",
            "Stucki small",
            "Stucki large",
            "Atkinson",
            "Burkes",
            "Sierra",
            "Sierra2",
            "Sierra2 4A",
            "Nakano",
        ]:
            kernel = get_kernel(algorithm)

            processed_image = error_diffusion(image, kernel, settings)

        elif algorithm == "Ostromoukhov" or algorithm == "Zhou-Fang":
            processed_image = variable_ed(image, algorithm, settings)

        elif algorithm == "None":
            # No processing, return the original image
            processed_image = image

        else:
            # Default case: No processing applied if algorithm is unknown
            print(
                f"Algorithm {algorithm} not recognized, no processing applied."
            )
            processed_image = image

        return processed_image

    def _send_result(self, image):
        self.storage.reset_view = self.reset
        self.storage.algorithm = self.algorithm
        self.storage.processed_image = image

        try:
            self.storage.generate_processed_pixmap()
        except Exception as e:
            print(e)

        # Go back to default behavior
        if self.reset:
            self.reset = False

    def _delayed_method_call(self, method, args, kwargs):
        method(self, *args, **kwargs)
