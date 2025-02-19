from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QApplication, QWidget


class FocusWidget(QWidget):
    def __init__(self):
        super().__init__()

        # An invisible widget to get focus on click
        # used to reset focus of the app as i cant seem
        # to find a cleaner way.

        self.setFixedSize(0, 0)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # reset everything
        self.setStyleSheet(
            """
            QWidget {
            background: transparent;
            border: none;
            margin: 0;
            padding:0;
            max-width: 0px;
            max-height: 0px;
            }
            """
        )

        self.setFocusPolicy(Qt.ClickFocus)

        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def focusInEvent(self, event):
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)


class FocusDebugger(QWidget):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            focused_widget = QApplication.focusWidget()
            if focused_widget:
                print(
                    f"Focused widget: {focused_widget.objectName()} ({focused_widget.__class__.__name__})"
                )
            else:
                print("No widget is focused")
        return super().eventFilter(obj, event)
