from collections.abc import Sequence, Collection


def rindex(seq: Sequence, items: Collection, start: int = None, end: int = None):
    if not seq or not items:
        return -1
    
    if start is None:
        start = 0
    
    if end is None:
        end = len(seq)
    
    for i, item in enumerate(reversed(seq[start:end])):
        if item in items:
            return end - i - 1

    return -1
