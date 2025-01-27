from PySide6.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class ToggleButton(QSlider):
    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)  # Horizontal slider
        self.setObjectName("toggleSlider")
        self.setMinimum(0)  # Minimum value
        self.setMaximum(1)  # Maximum value (only two states: 0 and 1)
        self.setSingleStep(1)  # Discrete steps (just 0 or 1)
        self.setTickPosition(QSlider.TickPosition.NoTicks)  # No ticks visible

    def mousePressEvent(self, event):
        """Override to toggle value on click without moving the slider"""
        if event.button() == Qt.MouseButton.LeftButton:  # Check for left mouse button
            # Toggle the value between 0 and 1
            new_value = 1 if self.value() == 0 else 0
            self.setValue(new_value)  # Set the new value to 0 or 1
            event.accept()  # Accept the event to stop it from propagating (normal slider behavior)
        else:
            super().mousePressEvent(event)  # Call the base class method for other buttons

class ToggleWithLabel(QWidget):
    toggleChanged = Signal(bool)

    def __init__(self, label="Serpentine", parent=None):
        super().__init__(parent)

        # Create the Toggle button (already styled)
        self.toggle = ToggleButton()  # Assuming ToggleButton is already defined
        self.toggle_label = QLabel(label)

        # Connect the slider’s valueChanged signal to the handler
        self.toggle.valueChanged.connect(self.on_toggle_changed)

        # Create the layout and add the toggle button with label
        toggle_hbox = QHBoxLayout()
        toggle_hbox.addWidget(self.toggle_label)
        toggle_hbox.addStretch()
        toggle_hbox.addWidget(self.toggle)

        # Set the layout for the widget
        self.setLayout(toggle_hbox)

    def on_toggle_changed(self, value):
        """Handle the toggle state change and emit the signal."""
        self.toggleChanged.emit(value == 1)

    def set_toggle_checked(self, checked: bool):
        """Sets the toggle to checked (1) or unchecked (0)."""
        self.toggle.setValue(1 if checked else 0)

    def is_toggle_checked(self):
        """Returns whether the toggle is checked (1) or unchecked (0)."""
        return self.toggle.value() == 1
