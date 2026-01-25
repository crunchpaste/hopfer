import logging
import time

import cv2
import numpy as np

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
    from hopfer.core.algorithms.cython_ops import (
        average,
        cast_f32_u16,
        equalize,
        lightness,
        luma,
        luminance,
        manual,
        normalize,
        value,
    )
except ImportError:
    from hopfer.core.algorithms.numba_ops import (
        average,
        lightness,
        luma,
        luminance,
        manual,
        value,
    )

from hopfer.core.algorithms.cython_ops import sierra24a

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
        self.processing = True
        start = time.perf_counter()

        if self.storage.resized is None:
            self.processing = False
            return

        try:
            self.res_queue.put({"type": "started_processing"})
            # step = self._determine_processing_step(step)

            # As grayscaling is done in parallel now and is so fast i merged the grayscaling and enchancement step into a single one to save on memory.
            if step == 0:
                if self.storage.original_grayscale:
                    gray_input = self.storage.resized.copy()
                    logger.debug(
                        "Skipping grayscale: Image is already grayscale."
                    )
                else:
                    gray_input = self._convert_to_grayscale(
                        self.storage.resized,
                        self.grayscale_mode,
                        self.grayscale_settings,
                    )
                    logger.debug(
                        f"Converted to grayscale via {self.grayscale_mode}"
                    )

                self.storage.enhanced_image = self._enhance_image(
                    gray_input, self.image_settings
                )
                logger.debug("Finished image adjustments")

            processed_image = self._process_algorithm()

        except Exception as e:
            logger.error(f"Error in processing: {e}")
            self._handle_processing_error()
            processed_image = self.storage.processed_image

        logger.debug(f"Processed in {time.perf_counter() - start:.3f}s")
        self._send_result(processed_image)

    # --- Helper Methods ---

    # def _determine_processing_step(self, step):
    #     """Determines whether conversion or enhancement should be performed."""
    #     convert = not self.storage.original_grayscale and step == 0
    #     enhance = step <= 1
    #     return 0 if convert else (1 if enhance else step)

    def _process_enhancement(self, grayscale_image, step):
        """Enhances the image based on the provided settings."""
        im_settings = self.image_settings
        if step < 1 and any(
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
                grayscale_image, im_settings
            )
            logger.debug("Finished image adjustments")
        else:
            self.storage.enhanced_image = grayscale_image
            logger.debug("Enhanced is just grayscale")

    def _process_algorithm(self):
        """Applies the processing algorithm if selected."""
        # Use enhanced_image if it exists, otherwise fallback to resized
        source = (
            self.storage.enhanced_image
            if self.storage.enhanced_image is not None
            else self.storage.resized
        )

        if source is None:
            logger.error("No image data available to process.")
            return None

        if self.algorithm != "None":
            return self._apply_algorithm(source, self.algorithm, self.settings)

        if source.dtype == np.uint16:
            return (source >> 8).astype(np.uint8)
        return source.astype(np.uint8)

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

        flag = image.dtype == np.uint8
        if mode == "Luminance":
            return luminance(image, out_8bit=flag)
        if mode == "Luma":
            return luma(image, out_8bit=flag)
        elif mode == "Average":
            return average(image, out_8bit=flag)
        elif mode == "Value":
            return value(image, out_8bit=flag)
        elif mode == "Lightness":
            return lightness(image, out_8bit=flag)
        elif mode == "Manual RGB":
            r = settings["r"]
            g = settings["g"]
            b = settings["b"]
            return manual(image, r, g, b)
        else:
            return luminance(image, out_8bit=flag)

    @staticmethod
    def _enhance_image(image, im_settings):
        """
        This is the method for image enchancements e.g. blurs.
        """

        logger.debug(f"Image arrived ad Enhancement as {image.dtype}")

        _brightness = im_settings["brightness"]
        if _brightness > 0:
            # using a log function makes the adjustment feel a bit more natural
            _brightness = 5 * (
                np.log(1 + (0.01 - 1) * _brightness) / np.log(0.01)
            )
        _brightness += 1

        _contrast = im_settings["contrast"]
        if _contrast > 0:
            # using a log function makes the adjustment feel a bit more natural
            _contrast = 5 * (np.log(1 + (0.01 - 1) * _contrast) / np.log(0.01))
        _contrast += 1

        if im_settings["normalize"]:
            # nomalize comes from the cython_ops module and is much faster than cv2 lut
            image = normalize(image, lut=True)
            logger.debug(f"Image left Normalize as {image.dtype}")

        if im_settings["equalize"]:
            if image.dtype == np.uint8:
                # cv2 is at least 2x faster for uint8
                cv2.equalizeHist(image, dst=image)
            else:
                # unfortunately it does not support uint16 so we use a cython implementation
                image = equalize(image)
            logger.debug(f"Image left EQ as {image.dtype}")

        if im_settings["bc_t"] and (_brightness != 1.0 or _contrast != 1.0):
            alpha = float(_contrast)
            if image.dtype == np.uint8:
                scale = 255
            else:
                scale = 65535

            beta = (scale / 2) * (1.0 - alpha) + (_brightness - 1.0) * scale
            # addWeighted is much much faster than any implementation i could come up and it does support uint16 ootb
            image = cv2.addWeighted(image, alpha, image, 0, beta, dst=image)
            logger.debug(f"Image left Contrast as {image.dtype}")

        if im_settings["blur_t"]:
            _box = int(im_settings["box"])
            _blur = int(im_settings["blur"])
            _median = int(im_settings["median"])
            if _median > 1:
                # medianBlur only supports uint8
                old_type = image.dtype
                if image.dtype != np.uint8 and _median > 5:
                    image = (image >> 8).astype(np.uint8)

                cv2.medianBlur(image, ksize=_median, dst=image)

                if old_type == np.uint16 and image.dtype != old_type:
                    logger.debug("Casting back to uint16")
                    image = image.astype(np.uint16) << 8

            if _box > 1:
                cv2.blur(image, ksize=(_box, _box), dst=image)
            if _blur > 1:
                if image.dtype == np.uint8:
                    cv2.stackBlur(image, ksize=(_blur, _blur), dst=image)
                else:
                    # if using uint16 stackBlur returns an overflowed image at kernel size 25 and up. therefore the image is cast to a float and the calculations are done like so.
                    img_f32 = image.astype(np.float32)
                    cv2.stackBlur(img_f32, ksize=(_blur, _blur), dst=img_f32)
                    # Slightly faster than casting and clipping with numpy, also a bit more memory efficient as we reuse the old array
                    cast_f32_u16(img_f32, image)
            logger.debug(f"Image left Blurs as {image.dtype}")

        if im_settings["unsharp_t"]:
            radius = im_settings["u_radius"] + 0.01
            strength = float(im_settings["u_strength"] * 3)

            if image.dtype == np.uint16:
                thresh = (im_settings["u_thresh"] / 10) * 65535

                blurred = cv2.GaussianBlur(image, ksize=(0, 0), sigmaX=radius)

                # diff in int32 to prevent wrap-around
                unsharp_mask = image.astype(np.int32) - blurred.astype(np.int32)

                if thresh > 0:
                    unsharp_mask[np.abs(unsharp_mask) < thresh] = 0

                res = cv2.addWeighted(
                    image.astype(np.float32),
                    1.0,
                    unsharp_mask.astype(np.float32),
                    strength,
                    0,
                )
                # clip and cast back to original buffer
                cast_f32_u16(res, image)
            else:
                thresh = (im_settings["u_thresh"] / 10) * 255

                blurred = cv2.GaussianBlur(image, ksize=(0, 0), sigmaX=radius)

                # int16 should be enough
                unsharp_mask = image.astype(np.int16) - blurred.astype(np.int16)

                if thresh > 0:
                    unsharp_mask[np.abs(unsharp_mask) < thresh] = 0

                res = cv2.addWeighted(
                    image.astype(np.float32),
                    1.0,
                    unsharp_mask.astype(np.float32),
                    strength,
                    0,
                )
                image[:] = np.clip(res, 0, 255).astype(np.uint8)
            logger.debug(f"Image left Unsharp as {image.dtype}")

        if im_settings["laplacian_t"]:
            strength = float(im_settings["l_strength"])
            size = int(im_settings["l_ksize"])
            if image.dtype == np.uint16:
                laplacian_mask = cv2.Laplacian(
                    image, ddepth=cv2.CV_32F, ksize=size
                )

                res = cv2.addWeighted(
                    image.astype(np.float32), 1.0, laplacian_mask, -strength, 0
                )

                cast_f32_u16(res, image)
            else:
                laplacian_mask = cv2.Laplacian(
                    image, ddepth=cv2.CV_32F, ksize=size
                )

                res = cv2.addWeighted(
                    image.astype(np.float32), 1.0, laplacian_mask, -strength, 0
                )

                image[:] = np.clip(res, 0, 255).astype(np.uint8)
            logger.debug(f"Image left Laplacian as {image.dtype}")

        return image

    @staticmethod
    def _apply_algorithm(image, algorithm, settings):
        """Apply the selected halftoning algorithm to the image via worker_h."""
        image_dtype = image.dtype
        logger.debug(f"Image arrived for processing as {image_dtype}")
        if algorithm == "Fixed threshold":
            # demote to uint8. no visual differences found.
            if image_dtype == np.uint16:
                image = (image >> 8).astype(np.uint8)
            processed_image = threshold(image, settings)

        elif algorithm == "Niblack threshold":
            # demote to uint8. no visual differences found.
            if image_dtype == np.uint16:
                image = (image >> 8).astype(np.uint8)
            processed_image = niblack_threshold(image, settings)

        elif algorithm == "Sauvola threshold":
            # demote to uint8. no visual differences found.
            if image_dtype == np.uint16:
                image = (image >> 8).astype(np.uint8)
            processed_image = sauvola_threshold(image, settings)

        elif algorithm == "Phansalkar threshold":
            # demote to uint8. no visual differences found.
            if image_dtype == np.uint16:
                image = (image >> 8).astype(np.uint8)
            processed_image = phansalkar_threshold(image, settings)

        elif algorithm == "Mezzotint uniform":
            if image_dtype == np.uint16:
                image = (image >> 8).astype(np.uint8)
            processed_image = mezzo(image, settings, mode="uniform")

        elif algorithm == "Mezzotint normal":
            # TODO: get that working
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
            # Expanding seems to give much better results in high contrast images and does not seem to slow the processing too much, so keeping it like that. Also saves me a bit of work on making a separate uint8 version.
            if image.dtype == np.uint8:
                image = (image).astype(np.uint16) << 8
            kernel = get_kernel(algorithm)
            processed_image = error_diffusion(image, kernel, settings)

        elif algorithm == "Sierra2 4A":
            # Expanding seems to give much better results in high contrast images and does not seem to slow the processing too much, so keeping it like that. Also saves me a bit of work on making a separate uint8 version.
            logger.debug(f"Image arrived at Sierra2 4A as {image.dtype}")
            if image.dtype == np.uint8:
                image = (image).astype(np.uint16) << 8
            processed_image = sierra24a(
                image, settings["diffusion_factor"], settings["serpentine"]
            )

        elif algorithm in ["Ostromoukhov", "Zhou-Fang"]:
            # Expanding seems to give much better results in high contrast images and does not seem to slow the processing too much, so keeping it like that. Also saves me a bit of work on making a separate uint8 version.
            if image.dtype == np.uint8:
                image = (image).astype(np.uint16) << 8
            processed_image = variable_ed(image, algorithm, settings)

        elif algorithm in ["Levien", "Nakano"]:
            # Expanding seems to give much better results in high contrast images and does not seem to slow the processing too much, so keeping it like that. Also saves me a bit of work on making a separate uint8 version.
            if image.dtype == np.uint8:
                image = (image).astype(np.uint16) << 8
            processed_image = edodf(image, algorithm, settings)

        elif algorithm == "None":
            # No processing, return the original image
            # Truncating it as Qt expects 8 bits anyway
            if image.dtype == np.uint16:
                image = (image >> 8).astype(np.uint8)
            processed_image = image

        else:
            logger.debug(f"{algorithm} not recognized, no processing applied.")
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
