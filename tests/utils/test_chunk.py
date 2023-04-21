import pytest

from utils.chunk import decoded_chunk_stream
from utils.chunk import CHARACTER_ENCODING_DEFAULT
from utils.chunk import resize_by_num_tokens


def test_decoded_chunk_stream_given_no_truncations():
    encoded_chunk_stream = [b'Hello, world!', b'Foo bar!']
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == [e.decode(CHARACTER_ENCODING_DEFAULT) for e in encoded_chunk_stream]


def test_decoded_chunk_stream_given_truncation(utf8_split):
    first, second = utf8_split
    encoded_chunk_stream = [b'Hello, world!' + first, second + b'Foo bar!']
    expected = [e.decode(CHARACTER_ENCODING_DEFAULT) for e in (b'Hello, world!', first + second + b'Foo bar!')]
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == expected


def test_decoded_chunk_stream_given_only_truncation(utf8_split):
    first, second = utf8_split
    encoded_chunk_stream = [first, second]
    expected = [e.decode(CHARACTER_ENCODING_DEFAULT) for e in (first + second,)]
    assert list(decoded_chunk_stream(encoded_chunk_stream)) == expected


def test_decoded_chunk_stream_given_multiple_truncations(utf8_split):
    first, second = utf8_split
    encoded_chunk_stream = [first, second, b'Hello' + first, second + b'world!', b'Foo bar!', first]
    expected = [e.decode(CHARACTER_ENCODING_DEFAULT) for e in (first + second, b'Hello', first + second + b'world!', b'Foo bar!')]
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


def test_resize_by_num_tokens():
    min_tokens = 15
    max_tokens = 25
    original = [
        'Hello, world!  This is     me',  # 9 tokens
        ' Bar baz! This is    my  last  sentence.   It is not   too  short.', # 21 tokens
        ' Foo bar!  This is my    second   sentence. I hope it is    long  enough. This    is a test.   Tests are fun.  And    fun is    good ', # 40 tokens
        'qux quux -  this is the last sentence.  It is not   too long.  Maybe   longer than   most', # 27 tokens
        '   but that is not    too big of   a problem, considering', # 14 tokens
    ]
    expected = [
        'Hello, world!  This is     me Bar baz! This is    my  last  sentence.',
        '   It is not   too  short. Foo bar!  This is my    second   sentence.',
        ' I hope it is    long  enough. This    is a test.   Tests are fun.',
        '  And    fun is    good qux quux -  this is the last sentence.',
        '  It is not   too long.  Maybe   longer than   most',
    ]
    actual = list(resize_by_num_tokens(original, min_tokens, max_tokens))
    assert actual == expected
