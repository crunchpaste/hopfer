import numpy as np
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QDoubleValidator, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

MAX_DIMENSION =  15_000

class DPIGroup(QGroupBox):
    size_changed = Signal(int, int)

    def __init__(self, title="Output DPI", parent=None):
        super().__init__(title, parent)
        # ... (rest of __init__) ...

        # ... (layouts, widgets, and connections remain the same) ...
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 25, 0, 0)

        self.width = MeasurementRow(label_text="Width")
        self.height = MeasurementRow(label_text="Height")
        self.dpi = MeasurementRow(label_text="DPI")
        self.ratio = 1
        self.px_size = [0, 0]

        self.layout.addWidget(self.width)
        self.layout.addWidget(self.height)

        self.setLayout(self.layout)

        self.width.input_field.textEdited.connect(self.calculate_height)
        self.height.input_field.textEdited.connect(self.calculate_width)

        self.width.input_field.editingFinished.connect(self.send_resize)
        self.height.input_field.editingFinished.connect(self.send_resize)

    def set_px_size(self, w, h):
        # ... (implementation remains the same) ...
        w = int(np.round(w))
        h = int(np.round(h))
        self.px_size = [w, h]
        self.ratio = w / h

        self.width.input_field.blockSignals(True)
        self.height.input_field.blockSignals(True)
        self.width.set_value(w)
        self.height.set_value(h)
        self.width.input_field.blockSignals(False)
        self.height.input_field.blockSignals(False)


    def _sync_internal_properties(self, w: float, h: float):
        """
        Helper to update internal properties after calculation,
        clipping values to MAX_DIMENSION (32768).
        """

        w_int = int(np.round(w))
        h_int = int(np.round(h))

        # --- CLIPPING LOGIC ---

        # 1. Check if the width exceeds the max dimension
        if w_int > MAX_DIMENSION:
            w_int = MAX_DIMENSION
            # Recalculate height based on the clipped width and fixed ratio
            h_int = int(np.round(w_int / self.ratio))

            # Update the UI field to reflect the clipped value
            self.width.input_field.blockSignals(True)
            self.width.set_value(w_int)
            self.width.input_field.blockSignals(False)

            self.height.input_field.blockSignals(True)
            self.height.set_value(h_int)
            self.height.input_field.blockSignals(False)

        # 2. Check if the height exceeds the max dimension (only if width wasn't already clipped)
        elif h_int > MAX_DIMENSION:
            h_int = MAX_DIMENSION
            # Recalculate width based on the clipped height and fixed ratio
            w_int = int(np.round(h_int * self.ratio))

            # Update the UI field to reflect the clipped value
            self.height.input_field.blockSignals(True)
            self.height.set_value(h_int)
            self.height.input_field.blockSignals(False)

            self.width.input_field.blockSignals(True)
            self.width.set_value(w_int)
            self.width.input_field.blockSignals(False)

        # ----------------------

        # Update internal properties (now clipped)
        self.px_size = [w_int, h_int]
        # self.ratio remains fixed.

    @Slot(str)
    def calculate_height(self, text):
        """Calculates height based on the edited width field and synchronizes properties."""
        new_width = self.width.get_value()

        if self.ratio > 0 and new_width > 0:
            new_height = new_width / self.ratio

            self.height.input_field.blockSignals(True)
            self.height.set_value(f"{new_height:.0f}")  # Update UI
            self.height.input_field.blockSignals(False)

            # --- SYNCHRONIZE AND CLIP INTERNAL PROPERTIES ---
            self._sync_internal_properties(new_width, new_height)

    @Slot(str)
    def calculate_width(self, text):
        """Calculates width based on the edited height field and synchronizes properties."""
        new_height = self.height.get_value()

        if self.ratio > 0 and new_height > 0:
            # Width = Ratio * Height
            new_width = self.ratio * new_height

            self.width.input_field.blockSignals(True)
            self.width.set_value(f"{new_width:.0f}")  # Update UI
            self.width.input_field.blockSignals(False)

            # --- SYNCHRONIZE AND CLIP INTERNAL PROPERTIES ---
            self._sync_internal_properties(new_width, new_height)

    def send_resize(self):
        # The stored px_size is already clipped by _sync_internal_properties
        self.size_changed.emit(self.px_size[0], self.px_size[1])


class MeasurementRow(QWidget):
    def __init__(self, label_text="Dimension:", default_unit="px", parent=None):
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        # self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.label.setMinimumWidth(50)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )

        spacer0 = QSpacerItem(
            15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )

        # Input Field (Numeric only)
        self.input_field = QLineEdit()
        self.validator = QDoubleValidator()
        self.validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        spacer1 = QSpacerItem(
            15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )
        self.input_field.setValidator(self.validator)
        self.input_field.setText("0.0")

        # Combo Box (Units)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["px", "mm", "cm", "inch"])

        index = self.unit_combo.findText(
            default_unit, Qt.MatchFlag.MatchExactly
        )
        if index != -1:
            self.unit_combo.setCurrentIndex(index)

        self.main_layout.addWidget(self.label)
        self.main_layout.addSpacerItem(spacer0)
        self.main_layout.addWidget(self.input_field)
        # self.main_layout.addSpacerItem(spacer1)
        # self.main_layout.addWidget(self.unit_combo)

    def get_value(self):
        try:
            return float(self.input_field.text())
        except ValueError:
            return 0.0

    def set_value(self, value):
        print("setting")
        # try:
        self.input_field.setText(str(value))
        # except ValueError:
        #     self.input_field.text = 10

    def get_unit(self):
        return self.unit_combo.currentText()
