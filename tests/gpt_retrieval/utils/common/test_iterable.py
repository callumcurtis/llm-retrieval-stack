import asyncio

import pytest

from gpt_retrieval.utils.common.iterable import batched
from gpt_retrieval.utils.common.iterable import ConcurrentAsyncMapper


def test_batched_given_empty_iterable():
    iterable = ()
    n = 1
    batches = list(batched(iterable, n))
    assert batches == []


def test_batched_given_iterable_of_size_n():
    iterable = [1, 2, 3]
    n = 3
    batches = list(batched(iterable, n))
    assert batches == [(1, 2, 3)]

def test_batched_given_iterable_of_size_n_plus_one():
    iterable = [1, 2, 3, 4]
    n = 3
    batches = list(batched(iterable, n))
    assert batches == [(1, 2, 3), (4,)]

def test_batched_given_iterable_of_size_n_minus_one():
    iterable = [1, 2, 3]
    n = 2
    batches = list(batched(iterable, n))
    assert batches == [(1, 2), (3,)]

def test_batched_given_invalid_n():
    iterable = [1, 2, 3]
    n = 0
    with pytest.raises(ValueError):
        list(batched(iterable, n))


def test_batched_given_multiple_batches():
    iterable = [1, 2, 3, 4, 5, 6]
    n = 2
    batches = list(batched(iterable, n))
    assert batches == [(1, 2), (3, 4), (5, 6)]


def test_concurrent_async_mapping_given_empty_iterable():
    iterable = ()
    n_complete = 0
    async def func(x):
        await asyncio.sleep(0)
        nonlocal n_complete
        n_complete += 1
    max_concurrent_tasks = 1
    mapper = ConcurrentAsyncMapper(func, max_concurrent_tasks)
    mapper(iterable)
    assert n_complete == 0


def test_concurrent_async_mapping_given_iterable_of_size_n():
    iterable = [1, 2, 3]
    n_complete = 0
    async def func(x):
        await asyncio.sleep(0)
        nonlocal n_complete
        n_complete += 1
    max_concurrent_tasks = 1
    mapper = ConcurrentAsyncMapper(func, max_concurrent_tasks)
    mapper(iterable)
    assert n_complete == 3


def test_concurrent_async_mapping_given_iterable_of_size_n_and_max_concurrent_tasks_of_n():
    iterable = [1, 2, 3]
    n_complete = 0
    async def func(x):
        await asyncio.sleep(0)
        nonlocal n_complete
        n_complete += 1
    max_concurrent_tasks = len(iterable)
    mapper = ConcurrentAsyncMapper(func, max_concurrent_tasks)
    mapper(iterable)
    assert n_complete == 3
