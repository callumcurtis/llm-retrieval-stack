import itertools
from typing import Iterable


def batched(iterable: Iterable, n: int):
    """Batch data into tuples of size n."""
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch
