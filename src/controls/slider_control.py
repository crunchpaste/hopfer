from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from controls.custom_range import RangeSlider
from helpers.decorators import debounce_alt


class SliderControl(QWidget):
    def __init__(self, label, range, value, div, double=False, precision=2, padding=10, stretch=False):
        super().__init__()

        self.div = div
        self.precision = precision
        self.is_dragging = False
        self.default = value
        self.double = double

        min_value, max_value = range[0], range[1]

        # Initialize slider and labels
        if self.double:
            self.slider = RangeSlider(Qt.Orientation.Horizontal)
        else:
            self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_value, max_value)
        self.slider.setValue(value)

        # Labels for the slider
        self.left_label = QLabel(label)

        self.reset = QPushButton("\ue5d5")
        self.reset.setObjectName("reset")
        self.reset.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.reset.clicked.connect(self.reset_to_default)
        self.reset.setVisible(False)

        if self.div:
            if self.double:
                self.right_label = QLabel(
                    f"{self.slider.value()[0] / self.div:.{self.precision}f} → {self.slider.value()[1] / self.div:.{self.precision}f}".format()
                )
            else:
                self.right_label = QLabel(
                    f"{self.slider.value() / self.div:.{self.precision}f}".format()
                )  # Initial value
        else:
            if self.double:
                self.right_label = QLabel(
                    f"{self.slider.value()[0]} → {self.slider.value()[1]}"
                )
            else:
                self.right_label = QLabel(f"{self.slider.value()}")

        # Connect slider signals
        self.slider.valueChanged.connect(self.update_value)
        self.slider.sliderPressed.connect(
            self.on_slider_pressed
        )  # Track when dragging starts
        self.slider.sliderReleased.connect(self.on_slider_released)

        # Layout for slider and labels
        self.slider_layout = QVBoxLayout()
        self.slider_labels = QHBoxLayout()
        self.slider_labels.addWidget(self.left_label)
        self.slider_labels.addWidget(self.reset)
        self.slider_labels.addStretch(1)
        self.slider_labels.addWidget(self.right_label)
        self.slider_layout.addLayout(self.slider_labels)
        self.slider_layout.addWidget(self.slider)

        if stretch:
            self.slider_layout.setContentsMargins(0, padding, 0, padding)

        self.setLayout(self.slider_layout)

    def update_value(self, value):
        """Update the right label with the current slider value."""
        if self.div:
            if self.double:
                self.right_label.setText(
                    f"{self.slider.value()[0] / self.div:.{self.precision}f} → {self.slider.value()[1] / self.div:.{self.precision}f}".format()
                )
            else:
                self.right_label.setText(
                    f"{value / self.div:.{self.precision}f}".format()
                )
        else:
            if self.double:
                self.right_label.setText(
                    f"{self.slider.value()[0]} → {self.slider.value()[1]}"
                )
            self.right_label.setText(f"{value}")

        self.show_reset(value)

    @debounce_alt(0.5)
    def show_reset(self, value):
        if value != self.default:
            self.reset.setVisible(True)
        else:
            self.reset.setVisible(False)

    def reset_to_default(self):
        self.slider.setValue(self.default)

    def on_slider_pressed(self):
        """Called when the slider starts being dragged."""
        self.is_dragging = True  # Mark that dragging has started

    def on_slider_released(self):
        """Called when the slider is released after dragging."""
        self.is_dragging = False  # Mark that dragging has finished
