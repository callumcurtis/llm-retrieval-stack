from utils.utf8 import truncation_point


def test_truncation_point_given_no_truncation(utf8_char):
    data = b'Hello, world!' + utf8_char
    assert truncation_point(data) == len(data)


def test_truncation_point_given_invalid_utf8():
    # Should not check if entire string is valid, only if it's truncated.
    data = b'Hello, \xffworld!'
    assert truncation_point(data) == len(data)


def test_truncation_point_given_truncated(utf8_truncation):
    expected = b'Hello, world!'
    data = expected + utf8_truncation 
    assert data[:truncation_point(data)] == expected


def test_truncation_point_given_only_continuation_bytes():
    data = b'\x80\x80\x80'
    assert truncation_point(data) == 0


def test_truncation_point_given_only_truncated(utf8_truncation):
    assert truncation_point(utf8_truncation) == 0