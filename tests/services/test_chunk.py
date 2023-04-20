import pytest

from services.chunk import decoded_chunk_stream
from services.chunk import ENCODING


def test_decoded_chunk_stream_given_no_truncations():
    encoded_chunk_stream = [b'Hello, world!', b'Foo bar!']
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == [e.decode(ENCODING) for e in encoded_chunk_stream]


def test_decoded_chunk_stream_given_truncation(utf8_split):
    first, second = utf8_split
    encoded_chunk_stream = [b'Hello, world!' + first, second + b'Foo bar!']
    expected = [e.decode(ENCODING) for e in (b'Hello, world!', first + second + b'Foo bar!')]
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == expected


def test_decoded_chunk_stream_given_only_truncation(utf8_split):
    first, second = utf8_split
    encoded_chunk_stream = [first, second]
    expected = [e.decode(ENCODING) for e in (first + second,)]
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == expected


def test_decoded_chunk_stream_given_multiple_truncations(utf8_split):
    first, second = utf8_split
    encoded_chunk_stream = [first, second, b'Hello' + first, second + b'world!', b'Foo bar!', first]
    expected = [e.decode(ENCODING) for e in (first + second, b'Hello', first + second + b'world!', b'Foo bar!')]
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == expected


def test_decoded_chunk_stream_given_only_continuation_bytes():
    encoded_chunk_stream = [b'\x80\x80\x80']
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == []


def test_decoded_chunk_stream_given_truncated_continuation_bytes():
    encoded_chunk_stream = [b'\x80\x80\x80', b'\x80']
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == []


def test_decoded_chunk_stream_given_invalid_utf8():
    encoded_chunk_stream = [b'Hello, \xffworld!']
    with pytest.raises(UnicodeDecodeError):
        list(decoded_chunk_stream(encoded_chunk_stream))


def test_decoded_chunk_stream_given_truncated_invalid_utf8():
    encoded_chunk_stream = [b'Hello, world!\xc3', b'\x28 Foo bar!']
    with pytest.raises(UnicodeDecodeError):
        list(decoded_chunk_stream(encoded_chunk_stream))