import time
import cv2
import numpy as np
import logging

from hopfer.helpers.kernels import get_kernel

try:
    from hopfer.core.algorithms.thresholdc import (
        niblack_threshold,
        phansalkar_threshold,
        sauvola_threshold,
        threshold,
    )
except ImportError:
    from hopfer.core.algorithms.threshold import (
        niblack_threshold,
        phansalkar_threshold,
        sauvola_threshold,
        threshold,
    )

try:
    from hopfer.core.algorithms.mezzoc import mezzo
except ImportError:
    from hopfer.core.algorithms.mezzo import mezzo

try:
    from hopfer.core.algorithms.bayerc import bayer, clustered
except ImportError:
    from hopfer.core.algorithms.bayer import bayer, clustered

try:
    from hopfer.core.algorithms.error_diffusionc import error_diffusion
except ImportError:
    from hopfer.core.algorithms.error_diffusion import error_diffusion

try:
    from hopfer.core.algorithms.variable_edc import variable_ed
except ImportError:
    from hopfer.core.algorithms.variable_ed import variable_ed

try:
    from hopfer.core.algorithms.edodfc import edodf
except ImportError:
    from hopfer.core.algorithms.edodf import edodf

try:
    from hopfer.core.algorithms.static import (
        average,
        lightness,
        luma,
        luminance,
        manual,
        value,
        sierra24a,
    )
except ImportError:
    from hopfer.core.algorithms.grayscale import (
        average,
        lightness,
        luma,
        luminance,
        manual,
        value,
    )

logger = logging.getLogger(__name__)


class ImageProcessor:
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
            "laplacian_t": False,
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

    def start(self, step=0):
        """
        The main method of the processor. It processes the image in a sequential manner
        then stores the result in the ImageStorage instance.
        """
        self.processing = True
        start = time.perf_counter()

        if self.storage.resized is None:
            self.processing = False
            return

        try:
            self.res_queue.put({"type": "started_processing"})

            # Determine the processing step based on grayscale mode and enhancement settings.
            step = self._determine_processing_step(step)

            # Perform processing steps sequentially.
            self._process_grayscale(step)
            self._process_enhancement(step)

            processed_image = self._process_algorithm()

        except Exception as e:
            print(e)
            self._handle_processing_error()
            processed_image = self.storage.processed_image

        logger.debug(f"Processed in {time.perf_counter() - start:.3f}s")
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
                self.storage.resized.copy(),
                self.grayscale_mode,
                self.grayscale_settings,
            )
        logger.debug("Converted to grayscale")

    def _process_enhancement(self, step):
        """Enhances the image based on the provided settings."""
        im_settings = self.image_settings
        if step <= 1 and any(
            im_settings[key]
            for key in [
                "normalize",
                "equalize",
                "bc_t",
                "blur_t",
                "unsharp_t",
                "laplacian_t",
            ]
        ):
            self.storage.enhanced_image = self._enhance_image(
                self.storage.grayscale_image, im_settings
            )
        elif step <= 1:
            self.storage.enhanced_image = self.storage.grayscale_image

        logger.debug("Finished image adjustments")

    def _process_algorithm(self):
        """Applies the processing algorithm if selected."""
        if self.algorithm != "None":
            return self._apply_algorithm(
                self.storage.enhanced_image, self.algorithm, self.settings
            )
        return (self.storage.enhanced_image >> 8).astype(np.uint8)

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
            r = settings["r"]
            g = settings["g"]
            b = settings["b"]
            return manual(image, r, g, b)
        else:
            return luminance(image)

    @staticmethod
    def _enhance_image(image, im_settings):
        """
        This is the method for image enchancements e.g. blurs.
        """

        _brightness = im_settings["brightness"]
        if _brightness > 0:
            # using a log function makes the adjustment feel a bit more natural
            _brightness = 5 * (np.log(1 + (0.01 - 1) * _brightness) / np.log(0.01))
        _brightness += 1

        _contrast = im_settings["contrast"]
        if _contrast > 0:
            # using a log function makes the adjustment feel a bit more natural
            _contrast = 5 * (np.log(1 + (0.01 - 1) * _contrast) / np.log(0.01))
        _contrast += 1

        if im_settings["normalize"]:
            low = np.min(image)
            high = np.max(image)

            if high > low:
                # LUT and equalizeHist require uint8
                img8 = (image >> 8).astype(np.uint8)
                lut = (np.arange(256) - (low >> 8)) * (255.0 / ((high - low) >> 8))
                lut = np.clip(lut, 0, 255).astype(np.uint8)
                img8 = cv2.LUT(img8, lut)
                image = img8.astype(np.uint16) << 8

        if im_settings["equalize"]:
            img8 = (image >> 8).astype(np.uint8)
            img8 = cv2.equalizeHist(img8)
            image = img8.astype(np.uint16) << 8

        if im_settings["bc_t"]:
            if _brightness != 1.0 or _contrast != 1.0:
                alpha = float(_contrast)
                beta = 32767.5 * (1.0 - alpha) + (_brightness - 1.0) * 65535.0
                image = cv2.addWeighted(image, alpha, image, 0, beta)

        if im_settings["blur_t"]:
            _box = int(im_settings["box"] * 2 - 1)
            _blur = int(im_settings["blur"] * 2 - 1)
            _median = int(im_settings["median"] * 2 - 1)
            if _median > 1:
                # medianBlur only supports uint8 or float32
                if image.dtype != np.uint8:
                    image = (image >> 8).astype(np.uint8)
                    image = cv2.medianBlur(image, ksize=_median)
            if _box > 0:
                if image.dtype != np.uint8:
                    image = (image >> 8).astype(np.uint8)
                image = cv2.blur(image, ksize=(_box, _box))
            if _blur > 0:
                if image.dtype != np.uint8:
                    image = (image >> 8).astype(np.uint8)
                image = cv2.stackBlur(image, ksize=(_blur, _blur))
            if image.dtype != np.uint16:
                image = image.astype(np.uint16) << 8

        if im_settings["unsharp_t"]:
            radius = im_settings["u_radius"] + 0.01
            strength = im_settings["u_strength"] * 2
            thresh = (im_settings["u_thresh"] / 10) * 65535

            blurred = cv2.GaussianBlur(image, ksize=(0, 0), sigmaX=radius)

            unsharp_mask = image.astype(np.int32) - blurred.astype(np.int32)

            if thresh > 0:
                bool_mask = np.abs(unsharp_mask) < thresh
                unsharp_mask[bool_mask] = 0

            res = cv2.addWeighted(
                image.astype(np.float32),
                1.0,
                unsharp_mask.astype(np.float32),
                strength,
                0,
            )
            image = np.clip(res, 0, 65535).astype(np.uint16)

        if im_settings["laplacian_t"]:
            strength = im_settings["l_strength"]

            laplacian_mask = cv2.Laplacian(image, ddepth=cv2.CV_32F, ksize=1)

            res = image.astype(np.float32) - (strength * laplacian_mask)

            image = np.clip(res, 0, 65535).astype(np.uint16)

        return image

    @staticmethod
    def _apply_algorithm(image, algorithm, settings):
        """Apply the selected halftoning algorithm to the image via worker_h."""

        logger.debug(f"Chose {algorithm}")

        if algorithm == "Fixed threshold":
            # demote to uint8. no visual differences found.
            image = (image >> 8).astype(np.uint8)
            processed_image = threshold(image, settings)

        elif algorithm == "Niblack threshold":
            # demote to uint8. no visual differences found.
            image = (image >> 8).astype(np.uint8)
            processed_image = niblack_threshold(image, settings)

        elif algorithm == "Sauvola threshold":
            # demote to uint8. no visual differences found.
            image = (image >> 8).astype(np.uint8)
            processed_image = sauvola_threshold(image, settings)

        elif algorithm == "Phansalkar threshold":
            # demote to uint8. no visual differences found.
            image = (image >> 8).astype(np.uint8)
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
        ]:
            kernel = get_kernel(algorithm)
            processed_image = error_diffusion(image, kernel, settings)

        elif algorithm == "Sierra2 4A":
            processed_image = sierra24a(
                image, settings["diffusion_factor"], settings["serpentine"]
            )

        elif algorithm in ["Ostromoukhov", "Zhou-Fang"]:
            processed_image = variable_ed(image, algorithm, settings)

        elif algorithm in ["Levien", "Nakano"]:
            processed_image = edodf(image, algorithm, settings)

        elif algorithm == "None":
            # No processing, return the original image
            processed_image = image

        else:
            # Default case: No processing applied if algorithm is unknown
            print(f"Algorithm {algorithm} not recognized, no processing applied.")
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
        self.reset = False

    def _delayed_method_call(self, method, args, kwargs):
        method(self, *args, **kwargs)
