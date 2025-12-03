from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from qframelesswindow import FramelessDialog

from controls.titlebar import DialogTitleBar
from controls.toggle import ToggleButton


class ImageResizeDialog(FramelessDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize image")
        self.setFixedSize(500, 400)
        self.setTitleBar(DialogTitleBar(self, label="Resize image"))

        # original pixel size and dpi
        self.original_w = parent.w
        self.original_h = parent.h
        self.original_ratio = self.original_w / self.original_h
        self.original_dpi = parent.dpi

        # Internal state, always stays pixels
        self.current_w_px = self.original_w
        self.current_h_px = self.original_h

        self._block_update = False

        self.int_validator = QIntValidator(1, 32000)
        self.float_validator = QDoubleValidator(0.0, 99999.0, 4)

        self.create_layout()
        self.setLayout(self.main_layout)

    def create_layout(self):
        grid = QGridLayout()
        grid.setContentsMargins(50, 95, 50, 50)
        grid.setVerticalSpacing(15)
        grid.setHorizontalSpacing(25)

        # labels
        grid.addWidget(QLabel("Width"), 0, 0)
        grid.addWidget(QLabel("Height"), 1, 0)
        grid.addWidget(QLabel("Keep ratio"), 2, 0)
        grid.addWidget(QLabel("Resolution"), 3, 0)

        # inputs
        self.w_input = QLineEdit()
        self.h_input = QLineEdit()
        self.res_input = QLineEdit(str(self.original_dpi))

        self.w_input.setValidator(self.int_validator)
        self.h_input.setValidator(self.int_validator)
        self.res_input.setValidator(self.float_validator)

        grid.addWidget(self.w_input, 0, 1)
        grid.addWidget(self.h_input, 1, 1)
        grid.addWidget(self.res_input, 3, 1)

        # aspect
        self.aspect = ToggleButton()
        self.aspect.setValue(1)
        grid.addWidget(self.aspect, 2, 1)

        # units
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["px", "mm", "cm", "in"])
        grid.addWidget(self.unit_combo, 0, 2, 2, 1)

        self.res_combo = QComboBox()
        self.res_combo.addItems(["px/in", "px/cm"])
        grid.addWidget(self.res_combo, 3, 2)

        # interpolation
        grid.addWidget(QLabel("Interpolation"), 4, 0)
        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItems(
            ["Nearest Neighbor", "Bilinear", "Bicubic", "Lanczos"]
        )
        self.interpolation_combo.setCurrentText("Bicubic")
        grid.addWidget(self.interpolation_combo, 4, 1, 1, 2)

        self.w_input.editingFinished.connect(self._apply_width)
        self.h_input.editingFinished.connect(self._apply_height)
        self.res_input.editingFinished.connect(self._apply_dpi)

        self.unit_combo.currentIndexChanged.connect(self._change_unit)
        self.res_combo.currentIndexChanged.connect(self._change_res_unit)

        # ok/cancel
        # TODO: fix formatting and defaults
        self.ok_btn = QPushButton("Resize")
        self.cancel_btn = QPushButton("Cancel")
        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.ok_btn)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(grid)
        self.main_layout.addStretch()
        self.main_layout.addLayout(btns)

        self._update_display()

    def _effective_dpi(self):
        try:
            dpi = float(self.res_input.text())
        except ValueError:
            dpi = self.original_dpi

        if self.res_combo.currentText() == "px/cm":
            return dpi * 2.54
        return dpi

    def _update_display(self):
        if self._block_update:
            return

        self._block_update = True

        dpi = self._effective_dpi()
        unit = self.unit_combo.currentText()

        w_in = self.current_w_px / dpi
        h_in = self.current_h_px / dpi

        if unit == "px":
            w = self.current_w_px
            h = self.current_h_px
        elif unit == "in":
            w = w_in
            h = h_in
        elif unit == "cm":
            w = w_in * 2.54
            h = h_in * 2.54
        else:
            w = w_in * 25.4
            h = h_in * 25.4

        self.w_input.setText(f"{w:.4f}" if unit != "px" else f"{int(round(w))}")
        self.h_input.setText(f"{h:.4f}" if unit != "px" else f"{int(round(h))}")

        self._block_update = False

    def _apply_width(self):
        if self._block_update:
            return

        try:
            val = float(self.w_input.text())
        except ValueError:
            return

        dpi = self._effective_dpi()
        unit = self.unit_combo.currentText()

        if unit == "px":
            w_in = val / dpi
        elif unit == "in":
            w_in = val
        elif unit == "cm":
            w_in = val / 2.54
        else:
            w_in = val / 25.4

        self.current_w_px = w_in * dpi

        if self.aspect.isChecked():
            self.current_h_px = self.current_w_px / self.original_ratio

        self._update_display()

    def _apply_height(self):
        if self._block_update:
            return

        try:
            val = float(self.h_input.text())
        except ValueError:
            return

        dpi = self._effective_dpi()
        unit = self.unit_combo.currentText()

        if unit == "px":
            h_in = val / dpi
        elif unit == "in":
            h_in = val
        elif unit == "cm":
            h_in = val / 2.54
        else:
            h_in = val / 25.4

        self.current_h_px = h_in * dpi

        if self.aspect.isChecked():
            self.current_w_px = self.current_h_px * self.original_ratio

        self._update_display()

    def _apply_dpi(self):
        if self._block_update:
            return

        try:
            new_dpi = self._effective_dpi()
        except ValueError:
            return

        unit = self.unit_combo.currentText()
        if unit != "px":
            w_in = self.current_w_px / self._effective_dpi()
            h_in = self.current_h_px / self._effective_dpi()

            self.current_w_px = w_in * new_dpi
            self.current_h_px = h_in * new_dpi

        self._update_display()

    def _change_unit(self):
        self._update_display()

    def _change_res_unit(self):
        try:
            dpi_val = float(self.res_input.text())
        except ValueError:
            return

        if self.res_combo.currentText() == "px/cm":
            new_val = dpi_val / 2.54
        else:
            new_val = dpi_val * 2.54

        self._block_update = True
        self.res_input.setText(f"{new_val:.4f}")
        self._block_update = False

        self._update_display()

    def get_result(self):
        return {
            "width_px": round(self.current_w_px),
            "height_px": round(self.current_h_px),
            "dpi": float(self.res_input.text()),
            "interpolation": self.interpolation_combo.currentText(),
        }
