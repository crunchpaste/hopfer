from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ToggleButton(QSlider):
    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        self.setObjectName("toggleSlider")
        self.setMinimum(0)
        self.setMaximum(1)
        self.setSingleStep(1)
        self.setTickPosition(QSlider.TickPosition.NoTicks)

    def mousePressEvent(self, event):
        """Override to toggle value on click without moving the slider"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
            event.accept()
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.toggle()
        else:
            super().keyPressEvent(event)

    def toggle(self):
        new_value = 1 if self.value() == 0 else 0
        self.setValue(new_value)

    def isChecked(self):
        # Directly check the status of the toggle.
        # Used in the resizing dialog as the label there is external.
        if self.value() == 1:
            return True
        else:
            return False


class ToggleWithLabel(QWidget):
    toggle_changed = Signal(bool)

    def __init__(self, label="Serpentine", parent=None):
        super().__init__(parent)

        self.toggle = ToggleButton()
        self.toggle.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.toggle_label = QLabel(label)

        self.toggle.valueChanged.connect(self.on_toggle_changed)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.toggle_label)
        self.layout.addStretch()
        self.layout.addWidget(self.toggle)

        self.setLayout(self.layout)

    def on_toggle_changed(self, value):
        """Handle the toggle state change and emit the signal."""
        self.toggle_changed.emit(value == 1)

    def set_toggle_checked(self, checked: bool):
        """Sets the toggle to checked (1) or unchecked (0)."""
        self.toggle.setValue(1 if checked else 0)

    def is_toggle_checked(self):
        """Returns whether the toggle is checked (1) or unchecked (0)."""
        return self.toggle.value() == 1


class ToggleContainer(QWidget):
    def __init__(self, label, items, parent=None):
        super().__init__(parent)

        self.items = items

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.toggle = ToggleWithLabel(label)
        self.layout.addWidget(self.toggle)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 5, 10, 5)
        self.layout.addWidget(self.content_widget)

        for item in self.items:
            self.content_layout.addWidget(item)

        self.content_widget.setVisible(False)

        self.toggle.toggle_changed.connect(self.toggle_content)

    def toggle_content(self, checked):
        """Show or hide the content based on toggle state."""
        self.content_widget.setVisible(checked)

    def add_widget(self, widget):
        """Convenience method to add widgets to the collapsible content."""
        self.content_layout.addWidget(widget)
