from concurrent.futures import Future
import sys
import threading
import PySide6.QtCore

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
import requests


def get(url):
    fut = Future()

    def _get(url):
        try:
            r = requests.get(url)
            fut.set_result(r)
        except Exception as e:
            fut.set_exception(e)

    t = threading.Thread(target=_get, args=(url,))
    t.start()
    while not fut.done():
        yield
    return fut.result()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World")
        self.setGeometry(100, 100, 640, 480)

        self.btn = QPushButton("Click me", self)
        self.btn.move(100, 100)
        self.btn.clicked.connect(self.on_click)

        self.label = QLabel(self)
        self.label.move(100, 200)
        self.label_count = 0

        self.startTimer(0)

    def timerEvent(self, event: PySide6.QtCore.QTimerEvent) -> None:
        self.label.setText(str(self.label_count))
        self.label_count += 1

        if hasattr(self, "generator"):
            try:
                next(self.generator)
            except StopIteration:
                delattr(self, "generator")

        return super().timerEvent(event)

    def on_click(self):
        def generator():
            gen = get("http://127.0.0.1:8080")
            while True:
                try:
                    yield next(gen)
                except StopIteration as resp:
                    self.btn.setText(resp.text)
                    return
                except requests.exceptions.ConnectionError as e:
                    self.btn.setText("Failed")
                    return
        self.generator = generator()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
