import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from controls.toggle import ToggleWithLabel


class ColorGroup(QGroupBox):
    def __init__(self, title="Preview colors", parent=None):
        super().__init__(title, parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 25, 0, 0)

        self.dark = ColorControl("Print", (34, 35, 35))
        self.light = ColorControl("Paper", (240, 246, 246))
        self.alpha = ColorControl("Alpha", (250, 128, 114))

        self.output = ToggleWithLabel(label="Output like preview")
        self.output_a = ToggleWithLabel(label="Alpha like preview")

        self.layout.addWidget(self.dark)
        self.layout.addWidget(self.light)
        self.layout.addWidget(self.alpha)
        self.layout.addWidget(self.output)
        # self.layout.addWidget(self.output_a)

        self.setLayout(self.layout)


class ColorControl(QWidget):
    color_changed = Signal(object, object)

    def __init__(self, label, color):
        super().__init__()

        self.color = np.array(color).astype(np.uint8)
        self.previous_color = QColor(color[0], color[1], color[2])

        self.label = QLabel(label)
        spacer0 = QSpacerItem(
            15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )
        spacer1 = QSpacerItem(
            15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )
        self.hex = QLineEdit()
        self.hex.setAlignment(Qt.AlignCenter)
        # could be used to limit the colors to hexes
        # but i've found it useful to insert css colors too
        # self.hex.setMaxLength(7)
        self.swatch = QPushButton()
        self.swatch.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.swatch.setFixedSize(28, 28)
        self.update_button_color(self.color)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.label)
        hbox.addSpacerItem(spacer0)
        hbox.addWidget(self.hex)
        hbox.addSpacerItem(spacer1)
        hbox.addWidget(self.swatch)

        # vbox = QVBoxLayout()
        # # vbox.addWidget(self.label)
        # vbox.addLayout(hbox)

        self.setLayout(hbox)

        self.swatch.clicked.connect(self.open_color_chooser)

        self.hex.editingFinished.connect(self.on_text_edit_finished)

    def on_text_edit_finished(self):
        """Handle the validation when editing is finished."""
        text = self.hex.text().strip()
        self.validate_and_update_color(text)

    def validate_and_update_color(self, text):
        """Validate the hex color format and update the color button if valid."""
        color, valid = self.is_valid_hex(text)
        if valid:
            self.previous_color = color  # Store the valid color
            self.color = np.array([color.red(), color.green(), color.blue()]).astype(
                np.uint8
            )
            self.update_button_color(color)
            self.color_changed.emit(self.color, self)
        else:
            self.update_button_color(self.previous_color)

    def update_button_color(self, color):
        """Update the button color based on the provided QColor or RGB array."""
        if isinstance(color, QColor):
            color_code = color.name()
        elif isinstance(color, np.ndarray):
            color_code = QColor(color[0], color[1], color[2]).name()

        self.swatch.setStyleSheet(
            f"background-color: {color_code}; border: 2px solid #f0f6f6;"
        )

        self.hex.setText(color_code)

    def open_color_chooser(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.color = np.array([color.red(), color.green(), color.blue()]).astype(
                np.uint8
            )
            self.update_button_color(color)
            self.color_changed.emit(self.color, self)

    def is_valid_hex(self, text):
        """Check if the text is a valid hex color format (#RRGGBB or #RGB)."""
        if text == "dark":
            color = QColor("#222323")
        elif text == "light":
            color = QColor("#f0f6f0")
        elif text == "accent":
            color = QColor("salmon")
        else:
            color = QColor(text)
            if not color.isValid():
                color = QColor(f"#{text}")
        return color, color.isValid()
