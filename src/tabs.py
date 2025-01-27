from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QCoreApplication, Signal
from controls.halftone_combo import HalftoneCombo
from controls.grayscale_combo import GrayscaleCombo
from controls.slider_control import SliderControl
from settings import *
from image_processor import ImageProcessor
from helpers.debounce import debounce



class HalftoneTab(QWidget):
    def __init__(self, processor):
        """
        Initialize the HalftoneTab widget, which allows users to select halftoning algorithms
        and configure related settings.
        """
        super().__init__()
        self.processor = processor
        self.current_algorithm = "None"

        self._initialize_ui()

    def _initialize_ui(self):
        self.layout = QVBoxLayout()

        # Add the combobox for algorithm selection
        self.combobox = HalftoneCombo()
        self.combobox.combobox.currentTextChanged.connect(self.on_algorithm_changed)
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
        if algorithm_name == "Threshold":
            return ThresholdSettings()
        elif algorithm_name in [
            "Floyd-Steinberg", "False Floyd-Steinberg", "Jarvis", "Stucki",
            "Stucki Small", "Stucki Large", "Atkinson", "Burkes", "Sierra",
            "Sierra2", "Sierra2 4A", "Nakano"
        ]:
            return ErrorDiffusionSettings()
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

    @debounce(0.5)
    def on_settings_changed(self, settings):
        """
        Trigger image processing when settings are changed.

        Args:
            settings (dict): The new settings for the algorithm.
        """
        print(f"Settings changed: {settings}")

        # Update processor settings and algorithm, then start processing
        self.processor.settings = settings
        self.processor.algorithm = self.current_algorithm
        self.processor.start()


class ImageTab(QWidget):
    file_opened_signal = Signal()

    def __init__(self, processor):
        """
        Initialize the ImageTab widget, which would offer some basic image adjustments in the future.
        """
        super().__init__()
        self.processor = processor
        self.processor.storage.grayscale_signal.connect(self.on_grayscale_signal)

        self._initialize_ui()

    def _initialize_ui(self):
        self.layout = QVBoxLayout()

        self.combobox = GrayscaleCombo()
        self.combobox.combobox.currentTextChanged.connect(self.on_mode_changed)
        self.sharpness = SliderControl("Sharpen", (0, 100), 0, 1)
        self.sharpness.slider.valueChanged.connect(self.on_settings_changed)
        self.sharpness.slider.sliderReleased.connect(lambda:                    self.on_settings_changed(self.sharpness.slider.value))


        self.layout.addWidget(self.combobox)
        self.layout.addWidget(self.sharpness)

        # Add stretch to the layout
        self.layout.addStretch()

        # Set the layout for the widget
        self.setLayout(self.layout)

    @debounce(0.5)
    def on_mode_changed(self, mode_name):
        """
        Handle the change of grayscaling mode and trigger re-processing.

        Args:
            mode_name (str): The selected grayscaling mode.
        """

        self.processor.grayscale_mode = mode_name
        self.processor.convert = True
        self.processor.start()

    @debounce(0.5)
    def on_settings_changed(self, value):
        """
        Trigger image processing when settings are changed.
        """
        storage = self.processor.storage
        if not self.sharpness.is_dragging:
            settings = {
                "sharpness": self.sharpness.slider.value()
            }
            self.processor.image_settings = settings
            if storage.original_image is not None:
                self.processor.start()

    def on_grayscale_signal(self, is_grayscale):
        if is_grayscale:
            self.combobox.combobox.setDisabled(is_grayscale)
            self.combobox.combobox.setCurrentIndex(0)
        else:
            self.combobox.combobox.setDisabled(is_grayscale)
