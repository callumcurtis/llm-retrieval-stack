import pytest

from gpt_retrieval.utils.common.sequence import index_any


@pytest.fixture(params=[True, False])
def reverse(request):
    return request.param


def test_index_any_given_empty_sequence(reverse):
    seq = []
    items = {1}
    expected = -1
    actual = index_any(seq, items, reverse=reverse)
    assert actual == expected


def test_index_any_given_empty_items(reverse):
    seq = [1, 2, 3, 4, 5]
    items = set()
    expected = -1
    actual = index_any(seq, items, reverse=reverse)
    assert actual == expected


def test_index_any_given_single_item(reverse):
    seq = [1, 2, 3, 4, 5]
    items = {4}
    expected = 3
    actual = index_any(seq, items, reverse=reverse)
    assert actual == expected


def test_index_any_given_multiple_items_and_no_reverse():
    seq = [1, 2, 3, 4, 5]
    items = {2, 4}
    expected = 1
    actual = index_any(seq, items)
    assert actual == expected


def test_index_any_given_multiple_items_and_reverse():
    seq = [1, 2, 3, 4, 5]
    items = {2, 4}
    expected = 3
    actual = index_any(seq, items, reverse=True)
    assert actual == expected


def test_index_any_given_no_match(reverse):
    seq = [1, 2, 3, 4, 5]
    items = {6}
    expected = -1
    actual = index_any(seq, items, reverse=reverse)
    assert actual == expected


def test_index_any_given_start_in(reverse):
    seq = [1, 2, 3, 4, 5]
    items = {2}
    expected = 1
    actual = index_any(seq, items, start=1, reverse=reverse)
    assert actual == expected


def test_index_any_given_start_out(reverse):
    seq = [1, 2, 3, 4, 5]
    items = {2}
    expected = -1
    actual = index_any(seq, items, start=2, reverse=reverse)
    assert actual == expected


def test_index_any_given_end_in(reverse):
    seq = [1, 2, 3, 4, 5]
    items = {3}
    expected = 2
    actual = index_any(seq, items, end=3, reverse=reverse)
    assert actual == expected


def test_index_any_given_end_out(reverse):
    seq = [1, 2, 3, 4, 5]
    items = {3}
    expected = -1
    actual = index_any(seq, items, end=2, reverse=reverse)
    assert actual == expected
