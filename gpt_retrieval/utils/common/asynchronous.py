import asyncio
import threading
import concurrent.futures
from types import CoroutineType

from .invariant import invariant


def background_event_loop_invariant_assertions(l: 'BackgroundEventLoop') -> None:
    assert l._closed == l._loop.is_closed()
    assert l._running == l._loop.is_running()
    assert l._running == (l._thread is not None and l._thread.is_alive())
    assert not (l._closed and l._running)


@invariant(background_event_loop_invariant_assertions)
class BackgroundEventLoop:

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = None
        self._closed = False
        self._running = False

    def start(self) -> None:
        assert not self._running
        assert not self._closed

        def run_within_background_thread():
            asyncio.set_event_loop(self._loop)
            # run until stop() is called
            self._loop.run_forever()

        self._thread = threading.Thread(
            target=run_within_background_thread,
        )
        self._thread.start()
        self._running = True

    def stop(self) -> None:
        assert self._running
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self._thread = None
        self._running = False

    def close(self) -> None:
        assert not self._closed
        if self._thread is not None:
            self.stop()
        self._loop.close()
        self._closed = True

    def create_task(self, coro: CoroutineType) -> concurrent.futures.Future:
        assert self._running
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def is_closed(self) -> bool:
        return self._closed

    def __enter__(self) -> None:
        self.start()

    def __exit__(self, *args) -> None:
        self.stop()

    def __del__(self) -> None:
        if not self._closed:
            self.close()
