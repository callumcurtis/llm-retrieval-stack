import pickle

import pytest

from utils.chunk import EncodedChunk
from utils.chunk import EncodedChunkStream
from utils.chunk import EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing
from utils.chunk import DecodedChunk
from utils.chunk import DecodedChunkStream
from utils.chunk import DecodedChunkStreamResizerByNumTokens
from utils.chunk import DecodedChunkStreamSplitWordHealer


@pytest.fixture
def encoded_chunk_stream_default_generator():
    return lambda: EncodedChunkStream()

@pytest.fixture
def encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator():
    return lambda: EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing()

@pytest.fixture
def decoded_chunk_stream_default_generator():
    return lambda: DecodedChunkStream()

@pytest.fixture
def decoded_chunk_stream_default_generator():
    return lambda: DecodedChunkStream()


def test_wrap_raw_encoded_chunk_stream_given_no_chunks(encoded_chunk_stream_default_generator):
    raw_encoded_chunk_stream = []
    expected = []
    actual = list(encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, 'utf-8'))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_one_chunk(encoded_chunk_stream_default_generator):
    raw_encoded_chunk_stream = [b'Hello, world!']
    encoding = 'utf-8'
    expected = [EncodedChunk(raw_encoded_chunk_stream[0], 0, len(raw_encoded_chunk_stream[0]), encoding)]
    actual = list(encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_multiple_chunks(encoded_chunk_stream_default_generator):
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_encoded_chunk in raw_encoded_chunk_stream:
        raw_encoded_chunk_start = expected[-1].end if expected else 0
        end = raw_encoded_chunk_start + len(raw_encoded_chunk)
        expected.append(EncodedChunk(raw_encoded_chunk, raw_encoded_chunk_start, end, encoding))
    actual = list(encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_start_byte(encoded_chunk_stream_default_generator):
    start = 74
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_encoded_chunk in raw_encoded_chunk_stream:
        raw_encoded_chunk_start = expected[-1].end if expected else start
        end = raw_encoded_chunk_start + len(raw_encoded_chunk)
        expected.append(EncodedChunk(raw_encoded_chunk, raw_encoded_chunk_start, end, encoding))
    actual = list(encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding, start))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_start_byte_iterable(encoded_chunk_stream_default_generator):
    starts = [74, 100, 43, 300]
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = [
        EncodedChunk(raw_encoded_chunk, start, start + len(raw_encoded_chunk), encoding)
        for raw_encoded_chunk, start in zip(raw_encoded_chunk_stream, starts)
    ]
    actual = list(encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding, starts))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_no_chunks(decoded_chunk_stream_default_generator):
    raw_decoded_chunk_stream = []
    expected = []
    actual = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, 'utf-8'))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_one_chunk(decoded_chunk_stream_default_generator):
    raw_decoded_chunk_stream = ['Hello, world!']
    encoding = 'utf-8'
    expected = [DecodedChunk(raw_decoded_chunk_stream[0], 0, len(raw_decoded_chunk_stream[0]), encoding)]
    actual = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_multiple_chunks(decoded_chunk_stream_default_generator):
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_decoded_chunk in raw_decoded_chunk_stream:
        raw_decoded_chunk_start = expected[-1].end if expected else 0
        end = raw_decoded_chunk_start + len(raw_decoded_chunk)
        expected.append(DecodedChunk(raw_decoded_chunk, raw_decoded_chunk_start, end, encoding))
    actual = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_start_byte(decoded_chunk_stream_default_generator):
    start = 43
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_decoded_chunk in raw_decoded_chunk_stream:
        raw_decoded_chunk_start = expected[-1].end if expected else start
        end = raw_decoded_chunk_start + len(raw_decoded_chunk)
        expected.append(DecodedChunk(raw_decoded_chunk, raw_decoded_chunk_start, end, encoding))
    actual = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding, start))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_start_byte_iterable(decoded_chunk_stream_default_generator):
    starts = [74, 100, 43, 300]
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = [
        DecodedChunk(raw_decoded_chunk, start, start + len(raw_decoded_chunk), encoding)
        for raw_decoded_chunk, start in zip(raw_decoded_chunk_stream, starts)
    ]
    actual = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding, starts))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_no_chunks(
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode([]))
    assert actual == []


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_no_truncations(
    encoded_chunk_stream_default_generator,
    decoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!']
    start = 8
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding, start)
    raw_decoded_chunk_stream = [chunk.decode(encoding) for chunk in raw_encoded_chunk_stream]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding, start))
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_truncation(
    utf8_split,
    encoded_chunk_stream_default_generator,
    decoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    first, second = utf8_split
    raw_encoded_chunk_stream = [
        b'Hello, world!' + first,
        second + b'Foo bar!',
    ]
    encoding = 'utf-8'
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    raw_decoded_chunk_stream = [
        'Hello, world!',
        (first + second + b'Foo bar!').decode(encoding),
    ]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding))
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_only_truncation(
    utf8_split,
    encoded_chunk_stream_default_generator,
    decoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    first, second = utf8_split
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [first, second]
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    raw_decode_chunk_stream = [(first + second).decode(encoding)]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decode_chunk_stream, encoding))
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_multiple_truncations(
    utf8_split,
    encoded_chunk_stream_default_generator,
    decoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
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
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    raw_decoded_chunk_stream = [
        (first + second).decode(encoding),
        'Hello',
        (first + second + b'world!').decode(encoding),
        'Foo bar!',
    ]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding))
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_only_continuation_bytes(
    encoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'\x80\x80\x80']
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    expected = []
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_truncated_continuation_bytes(
    encoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'\x80\x80\x80', b'\x80']
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    expected = []
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_invalid_utf8(
    encoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, \xffworld!']
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    with pytest.raises(UnicodeDecodeError):
        list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_truncated_invalid_utf8(
    encoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, world!\xc3', b'\x28 Foo bar!']
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding)
    with pytest.raises(UnicodeDecodeError):
        list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_contiguous_and_noncontiguous_chunks(
    utf8_split,
    encoded_chunk_stream_default_generator,
    decoded_chunk_stream_default_generator,
    encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator,
):
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
    encoded_chunk_stream = encoded_chunk_stream_default_generator().append_wrapped(raw_encoded_chunk_stream, encoding, encoded_starts)
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
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(raw_decoded_chunk_stream, encoding, decoded_starts))
    actual = list(encoded_to_decoded_chunk_stream_converter_with_truncation_healing_default_generator().decode(encoded_chunk_stream))
    assert actual == expected


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_no_chunks(
    decoded_chunk_stream_default_generator,
):
    actual = list(DecodedChunkStreamResizerByNumTokens(decoded_chunk_stream_default_generator()))
    assert actual == []


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_contiguous_chunks(
    decoded_chunk_stream_default_generator,
):
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
    original_text_stream = decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding)
    resized_text = [
        'Hello, world!  This is     me Bar baz! This is    my  last  sentence.',
        '   It is not   too  short. Foo bar!  This is my    second   sentence.',
        ' I hope it is    long  enough. This    is a test.   Tests are fun.',
        '  And    fun is    good qux quux -  this is the last sentence.',
        '  It is not   too long.  Maybe   longer than   most',
    ]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(resized_text, encoding))
    actual = list(DecodedChunkStreamResizerByNumTokens(original_text_stream, min_tokens, max_tokens))
    assert actual == expected


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_contiguous_and_noncontiguous_chunks(
    decoded_chunk_stream_default_generator,
):
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
    original_text_stream = decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding, original_starts)
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
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(resized_text, encoding, resized_starts))
    actual = list(DecodedChunkStreamResizerByNumTokens(original_text_stream, min_tokens, max_tokens))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_multiple_inner_splits(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    original_text = [
        "hello wor",
        "ld! This i",
        "s a test.",
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding))
    expected_text = [
        "hello ",
        "world! This ",
        "is a test.",
    ]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(expected_text, encoding))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_multiple_inner_splits_and_noncontiguous_chunks(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    original_text = [
        "greetings all and",
        " hello wor",
        "ld! This i",
        "s a test.",
    ]
    original_starts = [
        153,
        32,
        32 + len(original_text[1].encode(encoding)),
        594,
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding, original_starts))
    expected_text = [
        " all ",
        " hello ",
        "world! This ",
        " a test.",
    ]
    expected_starts = [
        153 + len("greetings".encode(encoding)),
        32,
        32 + len(expected_text[1].encode(encoding)),
        594 + len("s".encode(encoding)),
    ]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(expected_text, encoding, expected_starts))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_no_word_delimiters(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    original_text = [
        "hellotherethisisalongword",
        "world",
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding))
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_only_whitespace_after_healing(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    start = 36
    original_text = [
        "hello   the",
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding, start))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == []


def test_split_word_healing_in_decoded_chunk_stream_given_only_whitespace_before_healing(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    original_text = [
        "         \n\t  \t",
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == []


def test_split_word_healing_in_decoded_chunk_stream_given_single_word_with_trailing_delimiter_in_noncontiguous(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    original_text = [
        "hello ",
    ]
    start = 38
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding, start))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == []


def test_split_word_healing_in_decoded_chunk_stream_given_attempt_to_create_single_large_chunk(
    decoded_chunk_stream_default_generator,
):
    # make sure that prefixes cannot be accumulated to create a single large chunk
    # the way word delimiters are copied prevents this
    encoding = 'utf-8'
    original_text = [
        "   hello",
        "wor ld",
        "!",
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding))
    expected_text = [
        "hellowor ",
        "ld!",
    ]
    expected_text_start = len("   ".encode(encoding))
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(expected_text, encoding, expected_text_start))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_single_word_delimiter(
    decoded_chunk_stream_default_generator,
):
    encoding = 'utf-8'
    original_text = [
        "hello,world",
    ]
    original_text_stream = list(decoded_chunk_stream_default_generator().append_wrapped(original_text, encoding))
    expected_text = [
        "hello,",
    ]
    expected = list(decoded_chunk_stream_default_generator().append_wrapped(expected_text, encoding))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_decoded_chunk_stream_complete_transformation_pipeline_given_average_file_input(
    encoded_chunk_stream_default_generator,
    inputsdir,
):
    encoding = 'utf-8'
    chunk_size = 100
    original = (inputsdir / 'average-file.original.md').read_text(encoding=encoding)
    encoded = (inputsdir / 'average-file.original.md').read_bytes()
    encoded = [encoded[i:i + chunk_size] for i in range(0, len(encoded), chunk_size)]
    encoded = encoded_chunk_stream_default_generator().append_wrapped(encoded, encoding)
    decoded = encoded.decode()
    with open (inputsdir / 'average-file.expected.pickle', 'rb') as f:
        expected = pickle.load(f)
    actual = list(DecodedChunkStreamResizerByNumTokens(DecodedChunkStreamSplitWordHealer(decoded)))
    assert ''.join(a.text for a in actual) == original
    assert actual == expected
