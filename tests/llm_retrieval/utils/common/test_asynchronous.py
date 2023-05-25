import concurrent.futures
import asyncio

import pytest

from llm_retrieval.utils.common.asynchronous import BackgroundEventLoop


@pytest.fixture
def loop():
    loop = BackgroundEventLoop()
    yield loop
    if not loop.is_closed():
        loop.close()


def test_background_event_loop_given_multiple_restarts(loop):
    num_restarts = 3
    for _ in range(num_restarts):
        with loop:
            pass


def test_background_event_loop_given_start_after_close(loop):
    loop.close()
    with pytest.raises(AssertionError):
        loop.start()


def test_background_event_loop_given_stop_before_start(loop):
    with pytest.raises(AssertionError):
        loop.stop()


def test_background_event_loop_given_multiple_stops(loop):
    loop.start()
    num_stops = 3
    with pytest.raises(AssertionError):
        for _ in range(num_stops):
            loop.stop()


def test_background_event_loop_given_multiple_closes(loop):
    loop.start()
    num_closes = 3
    with pytest.raises(AssertionError):
        for _ in range(num_closes):
            loop.close()


def test_background_event_loop_given_multiple_starts(loop):
    loop.start()
    num_starts = 3
    with pytest.raises(AssertionError):
        for _ in range(num_starts):
            loop.start()


def test_background_event_loop_given_multiple_tasks(loop):
    with loop:
        num_tasks = 3
        tasks = []
        completed_tasks = 0

        async def task():
            await asyncio.sleep(0)
            nonlocal completed_tasks
            completed_tasks += 1

        for _ in range(num_tasks):
            tasks.append(loop.create_task(task()))

        concurrent.futures.wait(tasks)
        assert completed_tasks == num_tasks
