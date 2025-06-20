from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from controls.color_controls import ColorGroup
from controls.grayscale_combo import GrayscaleCombo
from controls.halftone_combo import HalftoneCombo
from controls.slider_control import SliderControl
from controls.toggle import ToggleContainer, ToggleWithLabel
from helpers.decorators import debounce
from settings import (
    BayerSettings,
    BetaSettings,
    ClusteredSettings,
    ErrorDiffusionSettings,
    GaussSettings,
    LevienSettings,
    MezzoSettings,
    NiblackSettings,
    NoneSettings,
    PhansalkarSettings,
    SauvolaSettings,
    ThresholdSettings,
)


class HalftoneTab(QWidget):
    def __init__(self, writer=None, window=None):
        """
        Initialize the HalftoneTab widget, which allows users to select halftoning algorithms
        and configure related settings.
        """
        super().__init__()
        self.writer = writer
        self.window = window
        self.current_algorithm = "None"

        self._initialize_ui()

    def _initialize_ui(self):
        self.layout = QVBoxLayout()

        # Add the combobox for algorithm selection
        self.combobox = HalftoneCombo()
        self.combobox.combobox.currentTextChanged.connect(
            self.on_algorithm_changed
        )
        self.layout.addWidget(self.combobox)

        # Initialize settings widget
        self.settings_widget = self._get_settings_widget(self.current_algorithm)
        self.layout.addWidget(self.settings_widget)

        self.setLayout(self.layout)

    def _get_settings_widget(self, algorithm_name):
        """
        Returns the appropriate settings widget for the selected algorithm.

        Args:
            algorithm_name (str): The selected halftoning algorithm name.

        Returns:
            QWidget: The corresponding settings widget.
        """
        if algorithm_name == "Fixed threshold":
            return ThresholdSettings()
        elif algorithm_name == "Niblack threshold":
            return NiblackSettings()
        elif algorithm_name == "Sauvola threshold":
            return SauvolaSettings()
        elif algorithm_name == "Phansalkar threshold":
            return PhansalkarSettings()
        elif algorithm_name == "Mezzotint uniform":
            return MezzoSettings()
        elif algorithm_name == "Mezzotint normal":
            return GaussSettings()
        elif algorithm_name == "Mezzotint beta":
            return BetaSettings()
        elif algorithm_name == "Clustered dot":
            return ClusteredSettings()
        elif algorithm_name == "Bayer":
            return BayerSettings()
        elif algorithm_name in [
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
            return ErrorDiffusionSettings()

        elif algorithm_name in [
            "Sierra2 4A",
            "Nakano",
            "Ostromoukhov",
            "Zhou-Fang",
        ]:
            return ErrorDiffusionSettings(serpentine=True)

        elif algorithm_name == "Levien":
            return LevienSettings()

        return NoneSettings()

    def on_algorithm_changed(self, algorithm_name):
        """
        Handle the algorithm change by updating the settings widget and triggering re-processing.

        Args:
            algorithm_name (str): The selected halftoning algorithm.
        """
        print(f"Algorithm changed to: {algorithm_name}")

        # Remove the old settings widget from the layout if it exists
        self._remove_old_settings_widget()

        # Dynamically create the new settings widget for the selected algorithm
        self.settings_widget = self._get_settings_widget(algorithm_name)

        # Update the current algorithm and add the new settings widget to the layout
        self.current_algorithm = algorithm_name
        self.layout.addWidget(self.settings_widget)

        # Connect the settings changed signal to the processing function
        self.settings_widget.settingsChanged.connect(self.on_settings_changed)
        QCoreApplication.processEvents()

        # Trigger settings change immediately to apply changes
        self.settings_widget.emit_settings_changed()

    def _remove_old_settings_widget(self):
        """Remove the previous settings widget from the layout."""
        if self.settings_widget is not None:
            self.settings_widget.setVisible(False)
            self.settings_widget.deleteLater()

    @debounce(0.15)
    def on_settings_changed(self, settings):
        """
        Trigger image processing when settings are changed.

        Args:
            settings (dict): The new settings for the algorithm.
        """
        print(f"Settings changed: {settings}")

        # Update processor settings and algorithm, then start processing
        algorithm = self.current_algorithm
        # self.processor.start(step=2)
        self.writer.send_halftone(algorithm, settings)


class ImageTab(QWidget):
    file_opened_signal = Signal()

    def __init__(self, writer=None, window=None):
        """
        Initialize the ImageTab widget, which would offer some basic image adjustments in the future.
        """
        super().__init__()
        self.writer = writer
        self.window = window
        self.window.reader.grayscale_signal.connect(self.on_grayscale_signal)
        self.sliders = []

        self._initialize_ui()

    def _initialize_ui(self):
        self.layout = QVBoxLayout()

        self.combobox = GrayscaleCombo()
        self.combobox.combobox.currentTextChanged.connect(self.on_mode_changed)

        self.rgb_widget = QWidget()
        rgb_layout = QVBoxLayout()
        self.red = SliderControl(
            "Red", (0, 100), 33, 100, padding=0, stretch=True
        )
        self.red.value_changed.connect(
            lambda: self.on_mode_changed("Manual RGB")
        )
        self.red.slider.sliderReleased.connect(
            lambda: self.on_mode_changed("Manual RGB")
        )
        self.green = SliderControl("Green", (0, 100), 33, 100, stretch=True)
        self.green.value_changed.connect(
            lambda: self.on_mode_changed("Manual RGB")
        )
        self.green.slider.sliderReleased.connect(
            lambda: self.on_mode_changed("Manual RGB")
        )
        self.blue = SliderControl("Blue", (0, 100), 33, 100, stretch=True)
        self.blue.value_changed.connect(
            lambda: self.on_mode_changed("Manual RGB")
        )
        self.blue.slider.sliderReleased.connect(
            lambda: self.on_mode_changed("Manual RGB")
        )

        rgb_layout.addWidget(self.red)
        rgb_layout.addWidget(self.green)
        rgb_layout.addWidget(self.blue)

        self.rgb_widget.setLayout(rgb_layout)

        # Initially set as invisible
        self.rgb_widget.setVisible(False)

        # a scroll area to hold all the possible image editing options
        scroll = QScrollArea()
        scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        scroll.setWidgetResizable(True)

        # container and layout to hold the options
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # numpy related toggles
        self.normalize = ToggleWithLabel(label="Normalize histogram")
        self.normalize.toggle_changed.connect(self.on_settings_changed)

        self.equalize = ToggleWithLabel(label="Equalize histogram")
        self.equalize.toggle_changed.connect(self.on_settings_changed)

        # pillow related sliders
        self.brightness = SliderControl("Brightness", (-100, 100), 0, 100)
        self.brightness.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.brightness)

        self.contrast = SliderControl("Contrast", (-100, 100), 0, 100)
        self.contrast.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.contrast)

        self.blur = SliderControl(
            "Gaussian filter", (0, 150), 0, 10, precision=1
        )
        self.blur.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.blur)

        self.median = SliderControl("Median filter", (1, 5), 1, 1, precision=1)
        self.median.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.median)

        self.wl = SliderControl("Wavelet levels", (0, 10), 0, 1, precision=1)
        self.wl.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.wl)

        self.wt = SliderControl("Wavelet threshold", (0, 50), 0, 1, precision=1)
        self.wt.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.wt)

        self.sharpness = SliderControl("Sharpen", (0, 100), 0, 1)
        self.sharpness.value_changed.connect(self.on_settings_changed)

        self.sliders.append(self.sharpness)

        self.u_radius = SliderControl("Radius", (0, 100), 30, 10, precision=1)
        self.u_radius.value_changed.connect(self.on_settings_changed)

        self.u_strenght = SliderControl("Strength", (0, 100), 25, 100)
        self.u_strenght.value_changed.connect(self.on_settings_changed)

        self.u_thresh = SliderControl("Threshold", (0, 20), 3, 1, precision=1)
        self.u_thresh.value_changed.connect(self.on_settings_changed)

        # Toggle containers
        self.bc_toggle = ToggleContainer(
            "Brightness/contrast", (self.brightness, self.contrast)
        )
        self.bc_toggle.toggle.toggle_changed.connect(
            lambda: self.on_settings_changed(sender=self.bc_toggle)
        )

        self.blur_toggle = ToggleContainer(
            "Blur/denoise", (self.blur, self.median)
        )
        self.blur_toggle.toggle.toggle_changed.connect(
            lambda: self.on_settings_changed(sender=self.blur_toggle)
        )

        self.unsharp_toggle = ToggleContainer(
            "Unsharp mask", (self.u_radius, self.u_strenght, self.u_thresh)
        )
        self.unsharp_toggle.toggle.toggle_changed.connect(
            lambda: self.on_settings_changed(sender=None)
        )

        self.layout.addWidget(self.combobox)
        layout.addWidget(self.rgb_widget)
        layout.addWidget(self.normalize)
        layout.addWidget(self.equalize)
        layout.addWidget(self.bc_toggle)
        layout.addWidget(self.blur_toggle)
        layout.addWidget(self.unsharp_toggle)
        layout.addStretch()

        container.setLayout(layout)
        scroll.setWidget(container)

        self.layout.addWidget(scroll)

        self.setLayout(self.layout)

    @debounce(0.15)
    def on_mode_changed(self, mode_name):
        """
        Handle the change of grayscaling mode and trigger re-processing.

        Args:
            mode_name (str): The selected grayscaling mode.
        """
        pass
        if mode_name == "Manual RGB":
            self.rgb_widget.setVisible(True)
            grayscale_settings = {
                "r": self.red.slider.value(),
                "g": self.green.slider.value(),
                "b": self.blue.slider.value(),
            }
        else:
            self.rgb_widget.setVisible(False)
            grayscale_settings = {}

        self.writer.send_grayscale(mode_name, grayscale_settings)

    @debounce(0.15)
    def on_settings_changed(self, value=None, sender=None):
        """
        Trigger image processing when settings are changed.
        """

        if sender is not None:  # noqa: SIM102
            # should happen only for containers. also i do prefer the loop separate
            # that's why the warning is ignored.
            if all(
                item.slider.value() == item.default for item in sender.items
            ):
                return
        pass
        # storage = self.processor.storage
        settings = {
            "normalize": self.normalize.is_toggle_checked(),
            "equalize": self.equalize.is_toggle_checked(),
            "bc_t": self.bc_toggle.toggle.is_toggle_checked(),
            "blur_t": self.blur_toggle.toggle.is_toggle_checked(),
            "unsharp_t": self.unsharp_toggle.toggle.is_toggle_checked(),
            "brightness": self.brightness.slider.value(),
            "contrast": self.contrast.slider.value(),
            "blur": self.blur.slider.value(),
            "median": self.median.slider.value(),
            "wl": self.wl.slider.value(),
            "wt": self.wt.slider.value(),
            "u_radius": self.u_radius.slider.value(),
            "u_strenght": self.u_strenght.slider.value(),
            "u_thresh": self.u_thresh.slider.value(),
            # "sharpness": self.sharpness.slider.value(),
        }

        self.writer.send_enhance(settings)

    def on_grayscale_signal(self, is_grayscale):
        if is_grayscale:
            self.combobox.combobox.setDisabled(is_grayscale)
            self.combobox.combobox.setCurrentIndex(0)
        else:
            self.combobox.combobox.setDisabled(is_grayscale)


class OutputTab(QWidget):
    def __init__(self, writer=None, window=None):
        """
        Initialize the HalftoneTab widget, which allows users to select halftoning algorithms
        and configure related settings.
        """
        super().__init__()

        self.writer = writer
        self.window = window

        self._initialize_ui()

    def _initialize_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 20, 15, 15)

        self.colors = ColorGroup()

        self.layout.addWidget(self.colors)

        self.colors.dark.color_changed.connect(self.on_color_change)
        self.colors.light.color_changed.connect(self.on_color_change)
        self.colors.alpha.color_changed.connect(self.on_color_change)
        self.colors.output.toggle_changed.connect(self.on_preview_change)

        self.layout.addStretch()

        self.setLayout(self.layout)

    def on_color_change(self, color, sender):
        """
        Slot to handle the color change. The sender is the widget (ColorControl)
        that emitted the signal.
        """
        # Check which ColorControl emitted the signal
        if sender == self.colors.dark:
            swatch = "dark"
        elif sender == self.colors.light:
            swatch = "light"
        elif sender == self.colors.alpha:
            swatch = "alpha"

        self.writer.send_color(color, swatch)

    def on_preview_change(self, value):
        self.writer.save_like_preview(value)
