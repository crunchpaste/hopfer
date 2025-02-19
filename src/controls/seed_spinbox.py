import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SeedSpinBox(QWidget):
    def __init__(self, label):
        super().__init__()
        layout_outer = QVBoxLayout()
        layout_inner = QHBoxLayout()
        layout_inner.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)

        self.spinbox = QSpinBox()

        self.spinbox.setRange(0, 9999)
        self.spinbox.setValue(3750)
        self.spinbox.setAlignment(Qt.AlignCenter)
        self.spinbox.setButtonSymbols(QSpinBox.PlusMinus)

        self.button = QPushButton("\ueb40")
        self.button.setObjectName("seed")
        self.button.setToolTip("New random seed")
        self.button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.button.clicked.connect(self.new_seed)

        layout_inner.addWidget(self.spinbox)
        layout_inner.addWidget(self.button)

        layout_outer.addWidget(self.label)
        layout_outer.addLayout(layout_inner)

        self.setLayout(layout_outer)

    def new_seed(self):
        seed = np.random.randint(0, 9999)
        self.spinbox.setValue(seed)
