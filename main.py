import sys
import asyncio


from PySide6.QtCore import QObject, QTimerEvent, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import requests
import aiohttp

import qEventloop



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World")
        self.setGeometry(100, 100, 640, 480)
    
        self.btn = QPushButton("Click me", self)
        self.btn.move(100, 100)
        self.btn.clicked.connect(self.on_click)
    
    def on_click(self):
        async def coro():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://baidu.com") as resp:
                    print(resp.status)
                    print((await resp.text())[:100])

        async def main():
            await asyncio.gather(*[coro() for i in range(1000)])
        print(loop.is_running())
        loop.create_task(main())
        loop.call_later(0.05, print, "hello")

    #     self.gen = gen()
    #     self.startTimer(0)
    
    # def timerEvent(self, event: QTimerEvent) -> None:
    #     print(next(self.gen))
    #     return super().timerEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qEventloop.QProactorLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    loop.run_forever()