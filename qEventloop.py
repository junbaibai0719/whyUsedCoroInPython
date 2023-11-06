import asyncio
from asyncio import events
import functools
import inspect
import sys
import threading
from PySide6.QtCore import QCoreApplication, QTimer, Slot
from PySide6.QtWidgets import QApplication

class QProactorLoop(asyncio.ProactorEventLoop):
    def __init__(self, app=None):
        super().__init__(QIocp())
        self._app = app or QCoreApplication.instance()
        self._timer = QTimer(self._app)
        self._timer.timeout.connect(self._run_once)
        self._timer.setInterval(0)

    def _run_once(self):
        if not self._stopping:
            super()._run_once()

    def _run_forever(self):
        self._check_closed()
        self._check_running()
        self._set_coroutine_origin_tracking(self._debug)
        self._thread_id = threading.get_ident()

        old_agen_hooks = sys.get_asyncgen_hooks()
        sys.set_asyncgen_hooks(firstiter=self._asyncgen_firstiter_hook,
                               finalizer=self._asyncgen_finalizer_hook)
        try:
            events._set_running_loop(self)
            self._timer.start()
            self._app.exec_()

        finally:
            self._stopping = False
            self._thread_id = None
            events._set_running_loop(None)
            self._set_coroutine_origin_tracking(False)
            sys.set_asyncgen_hooks(*old_agen_hooks)

    def run_forever(self) -> None:
        try:
            assert self._self_reading_future is None
            self.call_soon(self._loop_self_reading)
            self._run_forever()
        finally:
            if self._self_reading_future is not None:
                ov = self._self_reading_future._ov
                self._self_reading_future.cancel()
                # self_reading_future was just cancelled so if it hasn't been
                # finished yet, it never will be (it's possible that it has
                # already finished and its callback is waiting in the queue,
                # where it could still happen if the event loop is restarted).
                # Unregister it otherwise IocpProactor.close will wait for it
                # forever
                if ov is not None:
                    self._proactor._unregister(ov)
                self._self_reading_future = None

class QIocp(asyncio.IocpProactor):
    def select(self, timeout=None):
        if not self._results:
            self._poll(0)
        tmp = self._results
        self._results = []
        return tmp

def asyncClose(fn):
    """Allow to run async code before application is closed."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        f = asyncio.ensure_future(fn(*args, **kwargs))
        while not f.done():
            QApplication.instance().processEvents()

    return wrapper


def asyncSlot(*args, **kwargs):
    """Make a Qt async slot run on asyncio loop."""

    def _error_handler(task):
        try:
            task.result()
        except Exception:
            sys.excepthook(*sys.exc_info())

    def outer_decorator(fn):
        @Slot(*args, **kwargs)
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Qt ignores trailing args from a signal but python does
            # not so inspect the slot signature and if it's not
            # callable try removing args until it is.
            task = None
            while len(args):
                try:
                    inspect.signature(fn).bind(*args, **kwargs)
                except TypeError:
                    if len(args):
                        # Only convert args to a list if we need to pop()
                        args = list(args)
                        args.pop()
                        continue
                else:
                    task = asyncio.ensure_future(fn(*args, **kwargs))
                    task.add_done_callback(_error_handler)
                    break
            if task is None:
                raise TypeError(
                    "asyncSlot was not callable from Signal. Potential signature mismatch."
                )
            return task

        return wrapper

    return outer_decorator