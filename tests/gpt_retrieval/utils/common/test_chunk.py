import pickle

import pytest

from gpt_retrieval.utils.common.chunk import EncodedChunk
from gpt_retrieval.utils.common.chunk import EncodedChunkStream
from gpt_retrieval.utils.common.chunk import EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing
from gpt_retrieval.utils.common.chunk import DecodedChunk
from gpt_retrieval.utils.common.chunk import DecodedChunkStream
from gpt_retrieval.utils.common.chunk import DecodedChunkStreamResizerByNumTokens
from gpt_retrieval.utils.common.chunk import DecodedChunkStreamSplitWordHealer


def test_wrap_raw_encoded_chunk_stream_given_no_chunks():
    raw_encoded_chunk_stream = []
    encoding = 'utf-8'
    expected = []
    actual = list(EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_one_chunk():
    raw_encoded_chunk_stream = [b'Hello, world!']
    encoding = 'utf-8'
    expected = [EncodedChunk(raw_encoded_chunk_stream[0], 0, len(raw_encoded_chunk_stream[0]), encoding)]
    actual = list(EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_multiple_chunks():
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_encoded_chunk in raw_encoded_chunk_stream:
        raw_encoded_chunk_start = expected[-1].end if expected else 0
        end = raw_encoded_chunk_start + len(raw_encoded_chunk)
        expected.append(EncodedChunk(raw_encoded_chunk, raw_encoded_chunk_start, end, encoding))
    actual = list(EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream))
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
    actual = list(EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream, start))
    assert actual == expected


def test_wrap_raw_encoded_chunk_stream_given_start_byte_iterable():
    starts = [74, 100, 43, 300]
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!', b'', b'Baz qux! 123']
    encoding = 'utf-8'
    expected = [
        EncodedChunk(raw_encoded_chunk, start, start + len(raw_encoded_chunk), encoding)
        for raw_encoded_chunk, start in zip(raw_encoded_chunk_stream, starts)
    ]
    actual = list(EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream, starts))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_no_chunks():
    raw_decoded_chunk_stream = []
    encoding = 'utf-8'
    expected = []
    actual = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_one_chunk():
    raw_decoded_chunk_stream = ['Hello, world!']
    encoding = 'utf-8'
    expected = [DecodedChunk(raw_decoded_chunk_stream[0], 0, len(raw_decoded_chunk_stream[0]), encoding)]
    actual = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_multiple_chunks():
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = []
    for raw_decoded_chunk in raw_decoded_chunk_stream:
        raw_decoded_chunk_start = expected[-1].end if expected else 0
        end = raw_decoded_chunk_start + len(raw_decoded_chunk)
        expected.append(DecodedChunk(raw_decoded_chunk, raw_decoded_chunk_start, end, encoding))
    actual = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream))
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
    actual = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream, start))
    assert actual == expected


def test_wrap_raw_decoded_chunk_stream_given_start_byte_iterable():
    starts = [74, 100, 43, 300]
    raw_decoded_chunk_stream = ['Hello, world!', 'Foo bar!', '', 'Baz qux! 123']
    encoding = 'utf-8'
    expected = [
        DecodedChunk(raw_decoded_chunk, start, start + len(raw_decoded_chunk), encoding)
        for raw_decoded_chunk, start in zip(raw_decoded_chunk_stream, starts)
    ]
    actual = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream, starts))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_no_chunks():
    encoded_chunk_stream = EncodedChunkStream('utf-8')
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == []


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_no_truncations():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, world!', b'Foo bar!']
    start = 8
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream, start)
    raw_decoded_chunk_stream = [chunk.decode(encoding) for chunk in raw_encoded_chunk_stream]
    expected = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream, start))
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_truncation(utf8_split):
    first, second = utf8_split
    raw_encoded_chunk_stream = [
        b'Hello, world!' + first,
        second + b'Foo bar!',
    ]
    encoding = 'utf-8'
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    raw_decoded_chunk_stream = [
        'Hello, world!',
        (first + second + b'Foo bar!').decode(encoding),
    ]
    expected = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream))
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_only_truncation(utf8_split):
    first, second = utf8_split
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [first, second]
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    raw_decoded_chunk_stream = [(first + second).decode(encoding)]
    expected = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream))
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_multiple_truncations(utf8_split):
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
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    raw_decoded_chunk_stream = [
        (first + second).decode(encoding),
        'Hello',
        (first + second + b'world!').decode(encoding),
        'Foo bar!',
    ]
    expected = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream))
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_only_continuation_bytes():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'\x80\x80\x80']
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    expected = []
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_truncated_continuation_bytes():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'\x80\x80\x80', b'\x80']
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    expected = []
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_invalid_utf8():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, \xffworld!']
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    with pytest.raises(UnicodeDecodeError):
        list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_truncated_invalid_utf8():
    encoding = 'utf-8'
    raw_encoded_chunk_stream = [b'Hello, world!\xc3', b'\x28 Foo bar!']
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream)
    with pytest.raises(UnicodeDecodeError):
        list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))


def test_encoded_to_decoded_chunk_stream_with_truncation_healing_given_contiguous_and_noncontiguous_chunks(utf8_split):
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
    encoded_chunk_stream = EncodedChunkStream(encoding).append_wrapped(raw_encoded_chunk_stream, encoded_starts)
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
    expected = list(DecodedChunkStream(encoding).append_wrapped(raw_decoded_chunk_stream, decoded_starts))
    actual = list(EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream))
    assert actual == expected


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_no_chunks():
    actual = list(DecodedChunkStreamResizerByNumTokens(DecodedChunkStream('utf-8')))
    assert actual == []


def test_resize_decoded_chunks_in_stream_by_num_tokens_given_contiguous_chunks():
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
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text)
    resized_text = [
        'Hello, world!  This is     me Bar baz! This is    my  last  sentence.',
        '   It is not   too  short. Foo bar!  This is my    second   sentence.',
        ' I hope it is    long  enough. This    is a test.   Tests are fun.',
        '  And    fun is    good qux quux -  this is the last sentence.',
        '  It is not   too long.  Maybe   longer than   most',
    ]
    expected = list(DecodedChunkStream(encoding).append_wrapped(resized_text))
    actual = list(DecodedChunkStreamResizerByNumTokens(original_text_stream, min_tokens, max_tokens))
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
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text, original_starts)
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
    expected = list(DecodedChunkStream(encoding).append_wrapped(resized_text, resized_starts))
    actual = list(DecodedChunkStreamResizerByNumTokens(original_text_stream, min_tokens, max_tokens))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_multiple_inner_splits():
    encoding = 'utf-8'
    original_text = [
        "hello wor",
        "ld! This i",
        "s a test.",
    ]
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text)
    expected_text = [
        "hello ",
        "world! This ",
        "is a test.",
    ]
    expected = list(DecodedChunkStream(encoding).append_wrapped(expected_text))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_multiple_inner_splits_and_noncontiguous_chunks():
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
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text, original_starts)
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
    expected = list(DecodedChunkStream(encoding).append_wrapped(expected_text, expected_starts))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_no_word_delimiters():
    encoding = 'utf-8'
    original_text = [
        "hellotherethisisalongword",
        "world",
    ]
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text)
    expected = list(DecodedChunkStream(encoding).append_wrapped(original_text))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_only_whitespace_after_healing():
    encoding = 'utf-8'
    start = 36
    original_text = [
        "hello   the",
    ]
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text, start)
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == []


def test_split_word_healing_in_decoded_chunk_stream_given_only_whitespace_before_healing():
    encoding = 'utf-8'
    original_text = [
        "         \n\t  \t",
    ]
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text)
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == []


def test_split_word_healing_in_decoded_chunk_stream_given_single_word_with_trailing_delimiter_in_noncontiguous():
    encoding = 'utf-8'
    original_text = [
        "hello ",
    ]
    start = 38
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text, start)
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == []


def test_split_word_healing_in_decoded_chunk_stream_given_attempt_to_create_single_large_chunk():
    # make sure that prefixes cannot be accumulated to create a single large chunk
    # the way word delimiters are copied prevents this
    encoding = 'utf-8'
    original_text = [
        "   hello",
        "wor ld",
        "!",
    ]
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text)
    expected_text = [
        "hellowor ",
        "ld!",
    ]
    expected_text_start = len("   ".encode(encoding))
    expected = list(DecodedChunkStream(encoding).append_wrapped(expected_text, expected_text_start))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_split_word_healing_in_decoded_chunk_stream_given_single_word_delimiter():
    encoding = 'utf-8'
    original_text = [
        "hello,world",
    ]
    original_text_stream = DecodedChunkStream(encoding).append_wrapped(original_text)
    expected_text = [
        "hello,",
    ]
    expected = list(DecodedChunkStream(encoding).append_wrapped(expected_text))
    actual = list(DecodedChunkStreamSplitWordHealer(original_text_stream))
    assert actual == expected


def test_decoded_chunk_stream_complete_transformation_pipeline_given_average_file_input(inputsdir):
    encoding = 'utf-8'
    chunk_size = 500
    original = (inputsdir / 'average-file.original.md').read_text(encoding=encoding)
    encoded = (inputsdir / 'average-file.original.md').read_bytes()
    encoded = [encoded[i:i + chunk_size] for i in range(0, len(encoded), chunk_size)]
    encoded = EncodedChunkStream(encoding).append_wrapped(encoded)
    decoded = encoded.decode()
    with open (inputsdir / 'average-file.expected.pickle', 'rb') as f:
        expected = pickle.load(f)
    actual = list(DecodedChunkStreamResizerByNumTokens(DecodedChunkStreamSplitWordHealer(decoded)))
    assert ''.join(a.text for a in actual) == original
    assert actual == expected
