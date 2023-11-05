import sys
import asyncio


from PySide6.QtCore import QObject, QTimerEvent, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import requests

def gen():
    while True:
        yield 1


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World")
        self.setGeometry(100, 100, 640, 480)
    
        self.btn = QPushButton("Click me", self)
        self.btn.move(100, 100)
        self.btn.clicked.connect(self.on_click)

    def on_click(self):
        try:
            resp =  requests.get("http://127.0.0.1:8000/", timeout=5)        
            self.btn.setText(resp.text)
        except:
            self.btn.setText("Failed")

    #     self.gen = gen()
    #     self.startTimer(0)
    
    # def timerEvent(self, event: QTimerEvent) -> None:
    #     print(next(self.gen))
    #     return super().timerEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    asyncio.run(asyncio.sleep(1))