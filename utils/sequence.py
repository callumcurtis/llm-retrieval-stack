from collections.abc import Sequence, Collection


def index_any(seq: Sequence, items: Collection, start: int = None, end: int = None, reverse: bool = False):
    if not seq or not items:
        return -1
    
    if start is None:
        start = 0
    
    if end is None:
        end = len(seq)

    seq = seq[start:end]

    if reverse:
        seq = reversed(seq)

    for i, item in enumerate(seq):
        if item in items:
            return end - i - 1 if reverse else start + i

    return -1
