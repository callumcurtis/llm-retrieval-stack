from services.sequence import rindex


def test_rindex_given_empty_sequence():
    seq = []
    items = {1}
    expected = -1
    actual = rindex(seq, items)
    assert actual == expected


def test_rindex_given_empty_items():
    seq = [1, 2, 3, 4, 5]
    items = set()
    expected = -1
    actual = rindex(seq, items)
    assert actual == expected


def test_rindex_given_single_item():
    seq = [1, 2, 3, 4, 5]
    items = {4}
    expected = 3
    actual = rindex(seq, items)
    assert actual == expected


def test_rindex_given_multiple_items():
    seq = [1, 2, 3, 4, 5]
    items = {1, 3}
    expected = 2
    actual = rindex(seq, items)
    assert actual == expected


def test_rindex_given_no_match():
    seq = [1, 2, 3, 4, 5]
    items = {6}
    expected = -1
    actual = rindex(seq, items)
    assert actual == expected


def test_rindex_given_start_in():
    seq = [1, 2, 3, 4, 5]
    items = {2}
    expected = 1
    actual = rindex(seq, items, start=1)
    assert actual == expected


def test_rindex_given_start_out():
    seq = [1, 2, 3, 4, 5]
    items = {2}
    expected = -1
    actual = rindex(seq, items, start=2)
    assert actual == expected


def test_rindex_given_end_in():
    seq = [1, 2, 3, 4, 5]
    items = {3}
    expected = 2
    actual = rindex(seq, items, end=3)
    assert actual == expected


def test_rindex_given_end_out():
    seq = [1, 2, 3, 4, 5]
    items = {3}
    expected = -1
    actual = rindex(seq, items, end=2)
    assert actual == expected
