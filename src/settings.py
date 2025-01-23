from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from controls.slider_control import SliderControl
from controls.toggle import ToggleWithLabel

class HalftoneSettings(QWidget):
    settingsChanged = Signal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""
        raise NotImplementedError("This method should be implemented by subclasses.")

class NoneSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit empty settings for 'None' algorithm."""
        self.settingsChanged.emit({})  # No settings to change, just emit empty dictionary

class ThresholdSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The slider that controls the value for thresholding
        self.threshold_value = SliderControl("Threshold value", (0, 100), 50, 100)
        self.threshold_value.slider.valueChanged.connect(self.emit_settings_changed)
        self.threshold_value.slider.sliderReleased.connect(self.emit_settings_changed)

        # Add it to the layout
        self.layout.addWidget(self.threshold_value)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        if not self.threshold_value.is_dragging:
            settings = {
                "threshold_value": self.threshold_value.slider.value()
            }
            self.settingsChanged.emit(settings)

class ErrorDiffusionSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # Diffusion factor slider
        self.diffusion_factor = SliderControl("Diffusion factor", (0, 100), 100, 100)
        self.diffusion_factor.slider.valueChanged.connect(self.emit_settings_changed)
        self.diffusion_factor.slider.sliderReleased.connect(self.emit_settings_changed)

        # Serpentine toggle
        self.serpentine_toggle = ToggleWithLabel(label="Serpentine")
        self.serpentine_toggle.toggleChanged.connect(self.emit_settings_changed)

        # Add widgets to layout
        self.layout.addWidget(self.diffusion_factor)
        self.layout.addWidget(self.serpentine_toggle)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""
        if not self.diffusion_factor.is_dragging:
            settings = {
                "diffusion_factor": self.diffusion_factor.slider.value(),
                "serpentine": self.serpentine_toggle.is_toggle_checked()
            }
            self.settingsChanged.emit(settings)
