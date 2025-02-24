
from PySide6.QtCore import QObject, QTimer, Signal


class QueueReader(QObject):
    message_received = Signal(object)  # Signal to send messages to UI

    def __init__(self, queue, interval=50):
        super().__init__()
        self.queue = queue
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(interval)

    def check_queue(self):
        while not self.queue.empty():
            message = self.queue.get()
            print(message)
            # self.message_received.emit(message)
