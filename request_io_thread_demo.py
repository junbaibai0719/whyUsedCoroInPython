import sys
import threading
import PySide6.QtCore

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
import requests


class MyThread(PySide6.QtCore.QThread):
    finished = PySide6.QtCore.Signal(requests.Response)
    error = PySide6.QtCore.Signal(Exception)

    def __init__(self, url, resp_handler, error_handler):
        super().__init__()
        self.url = url
        self.resp_handler = resp_handler
        self.error_handler = error_handler
        self.finished.connect(resp_handler)
        self.error.connect(error_handler)

    def run(self):
        try:
            resp = requests.get(self.url, timeout=5)
            self.finished.emit(resp)
        except Exception as e:
            self.error.emit(e)



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
        def resp_handler(resp):
            self.btn.setText(resp.text)

        def error_handler(e):
            def resp_handler1(resp):
                def resp_handler2(resp):
                    self.btn.setText(resp.text)

                def error_handler2(e):
                    self.btn.setText("Failed2")

                self.btn.setText(resp.text)
                # 下一个请求
                self.t2 = MyThread("http://zhihu.com", resp_handler2, error_handler2)
                self.t2.start()


            def error_handler1(e):
                def resp_handler2(resp):
                    self.btn.setText(resp.text)

                def error_handler2(e):
                    self.btn.setText("Failed2")

                self.btn.setText("Failed1")
                # 下一个请求
                self.t2 = MyThread("http://zhihu.com", resp_handler2, error_handler2)
                self.t2.start()

            self.btn.setText("Failed")
            # 下一个请求
            self.t1 = MyThread("http://baidu.com", resp_handler1, error_handler1)
            self.t1.start()

        url = "http://127.0.0.1:8000"
        self.t = MyThread(url, resp_handler, error_handler)
        self.t.start()

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()