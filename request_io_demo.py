import sys
import PySide6.QtCore

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
import requests

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
        return super().timerEvent(event)

    def on_click(self):
        try:
            resp =  requests.get("http://127.0.0.1:8000/", timeout=5)        
            self.btn.setText(resp.text)
        except:
            self.btn.setText("Failed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()