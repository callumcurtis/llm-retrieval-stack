import pytest

from utils.chunk import encoded_to_decoded_chunk_stream
from utils.chunk import resize_decoded_chunks_in_stream_by_num_tokens
from utils.chunk import wrap_raw_encoded_chunk_stream
from utils.chunk import wrap_raw_decoded_chunk_stream
from utils.chunk import EncodedChunk
from utils.chunk import DecodedChunk


def test_wrap_raw_encoded_chunk_stream_given_no_chunks():
    raw_encoded_chunk_stream = []
    expected = []
    actual = list(wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, 'utf-8'))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_one_chunk():
    raw_encoded_chunk_stream = [b'Hello, world!']
    encoding = 'utf-8'
    expected = [EncodedChunk(raw_encoded_chunk_stream[0], 0, len(raw_encoded_chunk_stream[0]), encoding)]
    actual = list(wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_multiple_chunks():
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_encoded_chunk in raw_encoded_chunk_stream:
        raw_encoded_chunk_start = expected[-1].end if expected else 0
        end = raw_encoded_chunk_start + len(raw_encoded_chunk)
        expected.append(EncodedChunk(raw_encoded_chunk, raw_encoded_chunk_start, end, encoding))
    actual = list(wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_start_byte():
    start = 74
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_encoded_chunk in raw_encoded_chunk_stream:
        raw_encoded_chunk_start = expected[-1].end if expected else start
        end = raw_encoded_chunk_start + len(raw_encoded_chunk)
        expected.append(EncodedChunk(raw_encoded_chunk, raw_encoded_chunk_start, end, encoding))
    actual = list(wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding, start))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_start_byte_iterable():
    starts = [74, 100, 43, 300]
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = [
        EncodedChunk(raw_encoded_chunk, start, start + len(raw_encoded_chunk), encoding)
        for raw_encoded_chunk, start in zip(raw_encoded_chunk_stream, starts)
    ]
    actual = list(wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding, starts))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_no_chunks():
    raw_decoded_chunk_stream = []
    expected = []
    actual = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, 'utf-8'))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_one_chunk():
    raw_decoded_chunk_stream = ['Hello, world!']
    encoding = 'utf-8'
    expected = [DecodedChunk(raw_decoded_chunk_stream[0], 0, len(raw_decoded_chunk_stream[0]), encoding)]
    actual = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_multiple_chunks():
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_decoded_chunk in raw_decoded_chunk_stream:
        raw_decoded_chunk_start = expected[-1].end if expected else 0
        end = raw_decoded_chunk_start + len(raw_decoded_chunk)
        expected.append(DecodedChunk(raw_decoded_chunk, raw_decoded_chunk_start, end, encoding))
    actual = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_start_byte():
    start = 43
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_decoded_chunk in raw_decoded_chunk_stream:
        raw_decoded_chunk_start = expected[-1].end if expected else start
        end = raw_decoded_chunk_start + len(raw_decoded_chunk)
        expected.append(DecodedChunk(raw_decoded_chunk, raw_decoded_chunk_start, end, encoding))
    actual = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding, start))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_start_byte_iterable():
    starts = [74, 100, 43, 300]
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = [
        DecodedChunk(raw_decoded_chunk, start, start + len(raw_decoded_chunk), encoding)
        for raw_decoded_chunk, start in zip(raw_decoded_chunk_stream, starts)
    ]
    actual = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding, starts))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_no_chunks():
    actual = list(encoded_to_decoded_chunk_stream([]))
    assert actual == []


def test_encoded_to_decoded_chunk_stream_given_no_truncations():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!']
    start = 8
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding, start)
    raw_decoded_chunk_stream = [chunk.decode(encoding) for chunk in raw_encoded_chunk_stream]
    expected = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding, start))
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_truncation(utf8_split):
    first, second = utf8_split
    raw_encoded_chunk_stream = [
        b'Hello, world!' + first,
        second + b'Foo bar!',
    ]
    encoding = 'utf-8'
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    raw_decoded_chunk_stream = [
        'Hello, world!',
        (first + second + b'Foo bar!').decode(encoding),
    ]
    expected = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding))
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_only_truncation(utf8_split):
    first, second = utf8_split
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [first, second]
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    raw_decode_chunk_stream = [(first + second).decode(encoding)]
    expected = list(wrap_raw_decoded_chunk_stream(raw_decode_chunk_stream, encoding))
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_multiple_truncations(utf8_split):
    first, second = utf8_split
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [
        first,
        second,
        b'Hello' + first,
        second + b'world!',
        b'Foo bar!',
        first,
    ]
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    raw_decoded_chunk_stream = [
        (first + second).decode(encoding),
        'Hello',
        (first + second + b'world!').decode(encoding),
        'Foo bar!',
    ]
    expected = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding))
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_only_continuation_bytes():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'\x80\x80\x80']
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    expected = []
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_truncated_continuation_bytes():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'\x80\x80\x80', b'\x80']
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    expected = []
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_given_invalid_utf8():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, \xffworld!']
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    with pytest.raises(UnicodeDecodeError):
        list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))


def test_encoded_to_decoded_chunk_stream_given_truncated_invalid_utf8():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, world!\xc3', b'\x28 Foo bar!']
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding)
    with pytest.raises(UnicodeDecodeError):
        list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))


def test_encoded_to_decoded_chunk_stream_given_contiguous_and_noncontiguous_chunks(utf8_split):
    first, second = utf8_split
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [
        first,
        second,
        b'Hello' + first,
        second + b'world!',
        b'Foo bar!',
        first,
    ]
    encoded_starts = [
        32,
        32 + len(first),
        8,
        90,
        0,
        16,
    ]
    encoded_chunk_stream = wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream, encoding, encoded_starts)
    raw_decoded_chunk_stream = [
        (first + second).decode(encoding),
        'Hello',
        'world!',
        'Foo bar!',
    ]
    decoded_starts = [
        32,
        8,
        90,
        0,
    ]
    expected = list(wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream, encoding, decoded_starts))
    actual = list(encoded_to_decoded_chunk_stream(encoded_chunk_stream))
    assert actual == expected


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_no_chunks():
    actual = list(resize_decoded_chunks_in_stream_by_num_tokens([]))
    assert actual == []


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_contiguous_chunks():
    min_tokens = 15
    max_tokens = 25
    original_text = [
        'Hello, world!  This is     me',  # 9 tokens
        ' Bar baz! This is    my  last  sentence.   It is not   too  short.', # 21 tokens
        ' Foo bar!  This is my    second   sentence. I hope it is    long  enough. This    is a test.   Tests are fun.  And    fun is    good ', # 40 tokens
        'qux quux -  this is the last sentence.  It is not   too long.  Maybe   longer than   most', # 27 tokens
        '   but that is not    too big of   a problem, considering', # 14 tokens
    ]
    original_text_stream = wrap_raw_decoded_chunk_stream(original_text, 'utf-8')
    resized_text = [
        'Hello, world!  This is     me Bar baz! This is    my  last  sentence.',
        '   It is not   too  short. Foo bar!  This is my    second   sentence.',
        ' I hope it is    long  enough. This    is a test.   Tests are fun.',
        '  And    fun is    good qux quux -  this is the last sentence.',
        '  It is not   too long.  Maybe   longer than   most',
    ]
    expected = list(wrap_raw_decoded_chunk_stream(resized_text, 'utf-8'))
    actual = list(resize_decoded_chunks_in_stream_by_num_tokens(original_text_stream, min_tokens, max_tokens))
    assert actual == expected


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_contiguous_and_noncontiguous_chunks():
    encoding = 'utf-8'
    min_tokens = 15
    max_tokens = 25
    original_text = [
        'Hello, world!  This is     me',  # 9 tokens
        ' Bar baz! This is    my  last  sentence.   It is not   too  short.', # 21 tokens
        ' Foo bar!  This is my    second   sentence. I hope it is    long  enough. This    is a test.   Tests are fun.  And    fun is    good ', # 40 tokens
        'qux quux -  this is the last sentence.  It is not   too long.  Maybe   longer than   most', # 27 tokens
        '   but that is not    too big of   a problem, considering', # 14 tokens
    ]
    original_starts = [
        32,
        32 + len(original_text[0].encode(encoding)),
        8,
        325,
        74,
    ]
    original_text_stream = wrap_raw_decoded_chunk_stream(original_text, 'utf-8', original_starts)
    resized_text = [
        'Hello, world!  This is     me Bar baz! This is    my  last  sentence.',
        ' Foo bar!  This is my    second   sentence. I hope it is    long  enough.',
        ' This    is a test.   Tests are fun.  And    fun is    good ',
        'qux quux -  this is the last sentence.  It is not   too long.',
    ]
    resized_starts = [
        32,
        8,
        8 + len(resized_text[1].encode(encoding)),
        325,
    ]
    expected = list(wrap_raw_decoded_chunk_stream(resized_text, 'utf-8', resized_starts))
    actual = list(resize_decoded_chunks_in_stream_by_num_tokens(original_text_stream, min_tokens, max_tokens))
    assert actual == expected
