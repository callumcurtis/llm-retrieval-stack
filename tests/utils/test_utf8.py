import pytest

from utils.utf8 import is_continuation_byte
from utils.utf8 import leading_continuation_bytes
from utils.utf8 import truncation_point
from utils.utf8 import lstrip_continuation_bytes
from utils.utf8 import rstrip_continuation_bytes
from utils.utf8 import strip_continuation_bytes
from utils.utf8 import MAX_UTF8_CONTINUATION_BYTES_PER_CHAR


def test_is_continuation_byte_given_continuation_byte():
    assert is_continuation_byte(b'\x80'[0])


def test_is_continuation_byte_given_non_continuation_byte():
    assert not is_continuation_byte(b'\x00'[0])


def test_leading_continuation_bytes_given_empty_bytes():
    assert leading_continuation_bytes(b'') == 0


@pytest.mark.parametrize('continuation_bytes', [b'\x80' * i for i in range(1, MAX_UTF8_CONTINUATION_BYTES_PER_CHAR + 1)])
def test_leading_continuation_bytes_given_only_continuation_bytes(continuation_bytes):
    assert leading_continuation_bytes(continuation_bytes) == len(continuation_bytes)


def test_leading_continuation_bytes_given_no_continuation_bytes():
    assert leading_continuation_bytes(b'Hello, world!') == 0


def test_loading_continuation_bytes_given_continuation_bytes_and_non_continuation_bytes():
    assert leading_continuation_bytes(b'\x80Hello, world!') == 1


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


def test_lstrip_continuation_bytes_given_empty_bytes():
    assert lstrip_continuation_bytes(b'') == b''


def test_lstrip_continuation_bytes_given_no_continuation_bytes():
    assert lstrip_continuation_bytes(b'Hello, world!') == b'Hello, world!'


def test_lstrip_continuation_bytes_given_only_continuation_bytes():
    assert lstrip_continuation_bytes(b'\x80\x80\x80') == b''


def test_lstrip_continuation_bytes_given_continuation_bytes_before_non_continuation_bytes():
    assert lstrip_continuation_bytes(b'\x80Hello, world!') == b'Hello, world!'


def test_lstrip_continuation_bytes_given_continuation_bytes_after_non_continuation_bytes():
    assert lstrip_continuation_bytes(b'Hello, world!\x80') == b'Hello, world!\x80'


def test_rstrip_continuation_bytes_given_empty_bytes():
    assert rstrip_continuation_bytes(b'') == b''


def test_rstrip_continuation_bytes_given_no_continuation_bytes():
    assert rstrip_continuation_bytes(b'Hello, world!') == b'Hello, world!'


def test_rstrip_continuation_bytes_given_only_continuation_bytes():
    assert rstrip_continuation_bytes(b'\x80\x80\x80') == b''


def test_rstrip_continuation_bytes_given_continuation_bytes_before_non_continuation_bytes():
    assert rstrip_continuation_bytes(b'\x80Hello, world!') == b'\x80Hello, world!'


def test_rstrip_continuation_bytes_given_continuation_bytes_after_non_continuation_bytes():
    assert rstrip_continuation_bytes(b'Hello, world!\x80') == b'Hello, world!'


def test_strip_continuation_bytes_given_empty_bytes():
    assert strip_continuation_bytes(b'') == b''


def test_strip_continuation_bytes_given_no_continuation_bytes():
    assert strip_continuation_bytes(b'Hello, world!') == b'Hello, world!'


def test_strip_continuation_bytes_given_only_continuation_bytes():
    assert strip_continuation_bytes(b'\x80\x80\x80') == b''


def test_strip_continuation_bytes_given_continuation_bytes_before_non_continuation_bytes():
    assert strip_continuation_bytes(b'\x80Hello, world!') == b'Hello, world!'


def test_strip_continuation_bytes_given_continuation_bytes_after_non_continuation_bytes():
    assert strip_continuation_bytes(b'Hello, world!\x80') == b'Hello, world!'


def test_strip_continuation_bytes_given_continuation_bytes_before_and_after_non_continuation_bytes():
    assert strip_continuation_bytes(b'\x80Hello, world!\x80') == b'Hello, world!'
