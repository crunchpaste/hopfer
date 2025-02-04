from PySide6.QtWidgets import QSlider, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from helpers.debounce import debounce

class SliderControl(QWidget):
    def __init__(self, label, range, value, div):
        super().__init__()

        self.div = div
        self.is_dragging = False
        self.default = value

        min_value, max_value = range[0], range[1]

        # Initialize slider and labels
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
            self.right_label = QLabel(f"{self.slider.value() / self.div}")  # Initial value
        else:
            self.right_label = QLabel(f"{self.slider.value()}")
        # Connect slider signals
        self.slider.valueChanged.connect(self.update_value)
        self.slider.sliderPressed.connect(self.on_slider_pressed)  # Track when dragging starts
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

        self.setLayout(self.slider_layout)

    def update_value(self, value):
        """Update the right label with the current slider value."""
        if self.div:
            self.right_label.setText(f"{value / self.div}")
        else:
            self.right_label.setText(f"{value}")

        self.show_reset(value)

    @debounce(0.5)
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
        value = self.slider.value()
