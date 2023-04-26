import pytest

from utils.common.iterable import batched


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
