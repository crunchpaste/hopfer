from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from controls.seed_spinbox import SeedSpinBox
from controls.slider_control import SliderControl
from controls.toggle import ToggleWithLabel


class HalftoneSettings(QWidget):
    settingsChanged = Signal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""
        raise NotImplementedError(
            "This method should be implemented by subclasses."
        )


class NoneSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit empty settings for 'None' algorithm."""
        self.settingsChanged.emit(
            {}
        )  # No settings to change, just emit empty dictionary


class ThresholdSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The slider that controls the value for thresholding
        self.threshold_value = SliderControl(
            "Threshold value", (0, 100), 50, 100
        )
        self.threshold_value.value_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.threshold_value)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        settings = {"threshold_value": self.threshold_value.slider.value()}
        self.settingsChanged.emit(settings)


class NiblackSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The slider that controls the k range of the local threshold
        self.block_size = SliderControl("Block size", (2, 500), 25, False)
        self.block_size.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the k range of the local threshold
        self.k_factor = SliderControl("Local threshold", (1, 100), 10, 100)
        self.k_factor.value_changed.connect(self.emit_settings_changed)
        # Add it to the layout
        self.layout.addWidget(self.block_size)
        self.layout.addWidget(self.k_factor)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        settings = {
            "block_size": self.block_size.slider.value(),
            "k_factor": self.k_factor.slider.value(),
        }
        self.settingsChanged.emit(settings)


class SauvolaSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The slider that controls the k range of the local threshold
        self.block_size = SliderControl("Block size", (2, 500), 25, False)
        self.block_size.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the dynamic range of the local threshold
        self.dynamic_range = SliderControl("Dynamic range", (1, 100), 50, 100)
        self.dynamic_range.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the k range of the local threshold
        self.k_factor = SliderControl("Local threshold", (1, 100), 10, 100)
        self.k_factor.value_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.block_size)
        self.layout.addWidget(self.dynamic_range)
        self.layout.addWidget(self.k_factor)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        settings = {
            "block_size": self.block_size.slider.value(),
            "dynamic_range": self.dynamic_range.slider.value(),
            "k_factor": self.k_factor.slider.value(),
        }
        self.settingsChanged.emit(settings)


class PhansalkarSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The slider that controls the k range of the local threshold
        self.block_size = SliderControl("Block size", (2, 500), 25, False)
        self.block_size.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the dynamic range of the local threshold
        self.dynamic_range = SliderControl("Dynamic range", (1, 100), 50, 100)
        self.dynamic_range.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the k range of the local threshold
        self.k_factor = SliderControl("Local threshold", (1, 100), 25, 100)
        self.k_factor.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the p range of the local threshold
        self.p_factor = SliderControl(
            "Exponential influence", (1, 500), 30, 100
        )
        self.p_factor.value_changed.connect(self.emit_settings_changed)

        # The slider that controls the q range of the local threshold
        self.q_factor = SliderControl(
            "Exponential decay", (1, 100), 10, 10, precision=1
        )
        self.q_factor.value_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.block_size)
        self.layout.addWidget(self.dynamic_range)
        self.layout.addWidget(self.k_factor)
        self.layout.addWidget(self.p_factor)
        self.layout.addWidget(self.q_factor)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        if (
            not self.block_size.is_dragging
            and not self.dynamic_range.is_dragging
            and not self.k_factor.is_dragging
            and not self.p_factor.is_dragging
            and not self.q_factor.is_dragging
        ):
            settings = {
                "block_size": self.block_size.slider.value(),
                "dynamic_range": self.dynamic_range.slider.value(),
                "k_factor": self.k_factor.slider.value(),
                "p_factor": self.p_factor.slider.value(),
                "q_factor": self.q_factor.slider.value(),
            }
            self.settingsChanged.emit(settings)


class MezzoSettings(HalftoneSettings):
    def __init__(self, colors=None):
        super().__init__()

        self.range_slider = SliderControl(
            "Uniform range", (0, 100), (0, 100), 100, True, colors=colors
        )
        self.range_slider.value_changed.connect(self.emit_settings_changed)

        self.spin = SeedSpinBox("Random number seed")
        self.spin.spinbox.valueChanged.connect(self.emit_settings_changed)

        self.layout.addWidget(self.range_slider)
        self.layout.addWidget(self.spin)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        self.settingsChanged.emit(
            {
                "range": self.range_slider.slider.value(),
                "seed": self.spin.spinbox.value(),
            }
        )


class GaussSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()
        self.spin = SeedSpinBox("Random number seed")
        self.spin.spinbox.valueChanged.connect(self.emit_settings_changed)

        self.location = SliderControl("Peak location", (0, 100), 50, 100)
        self.location.value_changed.connect(self.emit_settings_changed)

        self.std = SliderControl("Starndard deviation", (0, 100), 50, 100)
        self.std.value_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.location)
        self.layout.addWidget(self.std)
        self.layout.addWidget(self.spin)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when the threshold value changes."""
        self.settingsChanged.emit(
            {
                "seed": self.spin.spinbox.value(),
                "location": self.location.slider.value(),
                "std": self.std.slider.value(),
            }
        )


class BetaSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()
        self.spin = SeedSpinBox("Random number seed")
        self.spin.spinbox.valueChanged.connect(self.emit_settings_changed)

        self.lock_toggle = ToggleWithLabel(label="Lock alpha/beta")
        self.lock_toggle.set_toggle_checked(True)

        self.alpha = SliderControl("Alpha", (1, 100), 5, 10, precision=1)
        self.alpha.value_changed.connect(self.emit_settings_changed)
        self.alpha.slider.valueChanged.connect(self.update_both)

        self.beta = SliderControl("Beta", (1, 100), 5, 10, precision=1)
        self.beta.value_changed.connect(self.emit_settings_changed)
        self.beta.slider.valueChanged.connect(self.update_both)

        self.layout.addWidget(self.lock_toggle)
        self.layout.addWidget(self.alpha)
        self.layout.addWidget(self.beta)
        self.layout.addWidget(self.spin)
        self.layout.addStretch()

    def update_both(self, value):
        if self.lock_toggle.is_toggle_checked():
            sender = self.sender()
            if sender == self.alpha.slider:
                self.beta.slider.setValue(self.alpha.slider.value())
            elif sender == self.beta.slider:
                self.alpha.slider.setValue(self.beta.slider.value())

    def emit_settings_changed(self):
        self.settingsChanged.emit(
            {
                "seed": self.spin.spinbox.value(),
                "alpha": self.alpha.slider.value(),
                "beta": self.beta.slider.value(),
            }
        )


class BayerSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The size of the Bayer matrix. Converted to the proper power of 2 in bayer.py and bayerc.py
        self.size = SliderControl("Matrix size", (1, 10), 1, False)
        self.size.value_changed.connect(self.emit_settings_changed)

        self.offset = SliderControl("Matrix offset", (-100, 100), 0, 100)
        self.offset.value_changed.connect(self.emit_settings_changed)

        self.perturbation = SliderControl(
            "Perturbation strength", (0, 100), 0, 100
        )
        self.perturbation.value_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.size)
        self.layout.addWidget(self.perturbation)
        self.layout.addWidget(self.offset)

        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""

        settings = {
            "size": self.size.slider.value(),
            "offset": self.offset.slider.value(),
            "perturbation": self.perturbation.slider.value(),
        }
        self.settingsChanged.emit(settings)


class ClusteredSettings(HalftoneSettings):
    def __init__(self):
        super().__init__()

        # The size of the Bayer matrix. Converted to the proper power of 2 in bayer.py and bayerc.py
        self.size = SliderControl("Dot size", (1, 100), 5, False)
        self.size.value_changed.connect(self.emit_settings_changed)

        self.angle = SliderControl("Dot angle", (0, 359), 90, False)
        self.angle.value_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.size)
        # self.layout.addWidget(self.angle)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""

        settings = {
            "size": self.size.slider.value(),
            "angle": self.angle.slider.value(),
        }
        self.settingsChanged.emit(settings)


class ErrorDiffusionSettings(HalftoneSettings):
    def __init__(self, serpentine=False):
        super().__init__()

        # Diffusion factor slider
        self.diffusion_factor = SliderControl(
            "Diffusion factor", (0, 100), 100, 100
        )
        self.diffusion_factor.value_changed.connect(self.emit_settings_changed)

        self.diffusion_factor.slider_layout.setContentsMargins(10, 10, 10, 10)
        # Serpentine toggle
        self.serpentine_toggle = ToggleWithLabel(label="Serpentine")
        if serpentine:
            self.serpentine_toggle.set_toggle_checked(True)
        self.serpentine_toggle.toggle_changed.connect(
            self.emit_settings_changed
        )

        self.noise_toggle = ToggleWithLabel(label="Prime w/ noise")
        self.noise_toggle.toggle_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.diffusion_factor)
        self.layout.addWidget(self.serpentine_toggle)
        self.layout.addWidget(self.noise_toggle)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""

        settings = {
            "diffusion_factor": self.diffusion_factor.slider.value(),
            "serpentine": self.serpentine_toggle.is_toggle_checked(),
            "noise": self.noise_toggle.is_toggle_checked(),
        }
        self.settingsChanged.emit(settings)


class LevienSettings(HalftoneSettings):
    def __init__(self, serpentine=False):
        super().__init__()

        # Diffusion factor slider
        self.diffusion_factor = SliderControl(
            "Diffusion factor", (0, 100), 100, 100
        )
        self.diffusion_factor.value_changed.connect(self.emit_settings_changed)

        self.diffusion_factor.slider_layout.setContentsMargins(10, 10, 10, 10)

        # Hysteresis slider

        self.hysteresis = SliderControl("Hysteresis", (0, 500), 50, 100)
        self.hysteresis.value_changed.connect(self.emit_settings_changed)

        self.hysteresis.slider_layout.setContentsMargins(10, 10, 10, 10)

        # Serpentine toggle
        self.serpentine_toggle = ToggleWithLabel(label="Serpentine")
        if serpentine:
            self.serpentine_toggle.set_toggle_checked(True)
        self.serpentine_toggle.toggle_changed.connect(
            self.emit_settings_changed
        )

        self.noise_toggle = ToggleWithLabel(label="Prime w/ noise")
        self.noise_toggle.toggle_changed.connect(self.emit_settings_changed)

        self.layout.addWidget(self.diffusion_factor)
        self.layout.addWidget(self.hysteresis)
        self.layout.addWidget(self.serpentine_toggle)
        self.layout.addWidget(self.noise_toggle)
        self.layout.addStretch()

    def emit_settings_changed(self):
        """Emit the current settings when any control changes."""

        settings = {
            "diffusion_factor": self.diffusion_factor.slider.value(),
            "hysteresis": self.hysteresis.slider.value(),
            "serpentine": self.serpentine_toggle.is_toggle_checked(),
            "noise": self.noise_toggle.is_toggle_checked(),
        }
        self.settingsChanged.emit(settings)
