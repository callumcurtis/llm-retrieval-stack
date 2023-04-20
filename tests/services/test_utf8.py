import pytest

from services.utf8 import truncation_point


UTF8_CHARS = [
    b'\x00',
    b'\x7f',
    b'\xc2\x80',
    b'\xdf\xbf',
    b'\xe0\xa0\x80',
    b'\xef\xbf\xbf',
    b'\xf0\x90\x80\x80',
    b'\xf4\x8f\xbf\xbf',
]


def truncations(data):
    return [data[:i] for i in range(1, len(data))]


@pytest.mark.parametrize('suffix', UTF8_CHARS)
def test_truncation_point_given_no_truncation(suffix):
    data = b'Hello, world!' + suffix
    assert truncation_point(data) == len(data)


def test_truncation_point_given_invalid_utf8():
    # Should not check if entire string is valid, only if it's truncated.
    data = b'Hello, \xffworld!'
    assert truncation_point(data) == len(data)


@pytest.mark.parametrize(
    'suffix',
    [t for b in UTF8_CHARS for t in truncations(b)]
)
def test_truncation_point_given_truncated(suffix):
    expected = b'Hello, world!'
    data = expected + suffix 
    assert data[:truncation_point(data)] == expected


def test_truncation_point_given_only_continuation_bytes():
    data = b'\x80\x80\x80'
    assert truncation_point(data) == 0


@pytest.mark.parametrize(
    'truncated',
    [t for b in UTF8_CHARS for t in truncations(b)]
)
def test_truncation_point_given_only_truncated(truncated):
    assert truncation_point(truncated) == 0