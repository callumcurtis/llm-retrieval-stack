import itertools
import threading
import concurrent.futures
from typing import Iterable, Callable, Awaitable, Generic, TypeVar

from .asynchronous import BackgroundEventLoop


def batched(iterable: Iterable, n: int):
    """Batch data into tuples of size n."""
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


_T = TypeVar('_T')


class ConcurrentAsyncMapper(Generic[_T]):

    def __init__(
        self,
        callable: Callable[[_T], Awaitable[None]],
        max_concurrent_tasks: int,
    ):
        self._callable = callable
        self._max_concurrent_tasks = max_concurrent_tasks
        self._loop = BackgroundEventLoop()

    def __call__(
        self,
        iterable: Iterable[_T],
    ) -> None:

        active_tasks = set()
        active_tasks_write_lock = threading.Lock()
        active_task_count_semaphore = threading.Semaphore(self._max_concurrent_tasks)
        continue_discarding_tasks = threading.Event()
        continue_discarding_tasks.set()

        def cleanup_task(task: concurrent.futures.Future) -> None:
            if continue_discarding_tasks.is_set():
                with active_tasks_write_lock:
                    if continue_discarding_tasks.is_set():
                        active_tasks.discard(task)
            active_task_count_semaphore.release()

        with self._loop:

            for item in iterable:
                active_task_count_semaphore.acquire()
                task = self._loop.create_task(self._callable(item))
                with active_tasks_write_lock:
                    active_tasks.add(task)
                task.add_done_callback(cleanup_task)

            continue_discarding_tasks.clear()

            concurrent.futures.wait(self._tasks)
