import threading
import time
import traceback
from typing import List
import asyncio
import functools
import sys

import aiohttp

# from PyQt5.QtWidgets import (
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QApplication
)

from qEventloop import QProactorLoop, asyncSlot


# def asyncClose(fn):
#     """Allow to run async code before application is closed."""

#     @functools.wraps(fn)
#     def wrapper(*args, **kwargs):
#         fn(*args, **kwargs)
#         QApplication.instance().processEvents()

#     return wrapper


class MainWindow(QWidget):
    """Main window."""

    _DEF_URL = "https://jsonplaceholder.typicode.com/todos/1"
    """str: Default URL."""

    _SESSION_TIMEOUT = 10
    """float: Session timeout."""

    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())

        self.lblStatus = QLabel("Idle", self)
        self.layout().addWidget(self.lblStatus)

        self.editUrl = QLineEdit(self._DEF_URL, self)
        self.layout().addWidget(self.editUrl)

        self.editResponse = QTextEdit("", self)
        self.layout().addWidget(self.editResponse)

        self.btnFetch = QPushButton("Fetch", self)
        self.btnFetch.clicked.connect(self.on_btnFetch_clicked)
        self.layout().addWidget(self.btnFetch)

        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(
            loop=self.loop,
            timeout=aiohttp.ClientTimeout(total=self._SESSION_TIMEOUT),
        )
        self.tasks:List[asyncio.Task] = []
    
    @asyncSlot()
    async def on_btnFetch_clicked(self):
        tasks = []
        async def coro():
            async with self.session.get("http://localhost:8000") as response:
                    await response.text()
        for _ in range(100):
            tasks.append(coro())
        await asyncio.gather(*tasks)



async def main():
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    app = QApplication.instance()
    loop = asyncio.get_event_loop()
    print(loop)
    future = asyncio.Future()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )

    mainWindow = MainWindow()
    mainWindow.show()
    await future
    # loop.call_later(1, lambda:print("hello world"))
    # app.exec()
    return True


if __name__ == "__main__":
    app = QApplication()
    loop = QProactorLoop()
    asyncio.set_event_loop(loop)
    loop.create_task(main())
    loop.run_forever()
