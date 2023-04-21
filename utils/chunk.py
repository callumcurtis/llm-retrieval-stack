from typing import Iterable
from typing import Union

import tiktoken

from .utf8 import truncation_point
from .utf8 import lstrip_continuation_bytes
from .sequence import rindex


TOKEN_ENCODING = 'cl100k_base'
PREFERRED_CHUNK_DELIMITERS = '.!?\n'
MIN_TOKENS_PER_CHUNK_DEFAULT = 10
MAX_TOKENS_PER_CHUNK_DEFAULT = 200

tokenizer = tiktoken.get_encoding(TOKEN_ENCODING)


class DecodedChunk:
    """A decoded chunk of text.
    
    Attributes:
        text: The decoded text.
        start: The start index of the chunk in the original bytes.
        end: The end index of the chunk in the original bytes.
        encoding: The encoding of the text.
    """

    def __init__(self, text: str, start: int, end: int, encoding: str):
        self._text = text
        self._start = start
        self._end = end
        self._encoding = encoding

    @property
    def text(self) -> str:
        return self._text

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end
    
    @property
    def encoding(self) -> str:
        return self._encoding
    
    def __eq__(self, other):
        if not isinstance(other, DecodedChunk):
            return False
        return self.text == other.text and self.start == other.start and self.end == other.end

    def __repr__(self):
        return f'DecodedChunk({self.text!r}, {self.start!r}, {self.end!r}, {self.encoding!r})'


class EncodedChunk:
    """An encoded chunk of bytes.
    
    Attributes:
        bytes: The encoded bytes.
        start: The start index of the chunk in the original bytes.
        end: The end index of the chunk in the original bytes.
        encoding: The encoding of the bytes.
    """

    def __init__(self, bytes: bytes, start: int, end: int, encoding: str):
        self._bytes = bytes
        self._start = start
        self._end = end
        self._encoding = encoding

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end
    
    @property
    def encoding(self) -> str:
        return self._encoding
    
    def __eq__(self, other):
        if not isinstance(other, EncodedChunk):
            return False
        return self.bytes == other.bytes and self.start == other.start and self.end == other.end
    
    def __repr__(self):
        return f'EncodedChunk({self.bytes!r}, {self.start!r}, {self.end!r}, {self.encoding!r})'


RawEncodedChunkStream = Iterable[bytes]
EncodedChunkStream = Iterable[EncodedChunk]

RawDecodedChunkStream = Iterable[str]
DecodedChunkStream = Iterable[DecodedChunk]


def wrap_raw_encoded_chunk_stream(raw_encoded_chunk_stream: RawEncodedChunkStream, encoding: str, start: Union[int, Iterable[int]] = 0) -> EncodedChunkStream:
    """Wrap a stream of raw encoded chunks into a stream of encoded chunks.

    Args:
        raw_encoded_chunk_stream: A stream of raw encoded chunks.
        encoding: The encoding of the chunks.
        start: The start index of the first chunk in the original bytes or a stream of start indices, one for each chunk.
    """

    # Note: though similar to wrap_raw_decoded_chunk_stream, the two have not been refactored into a single function
    # because their similarity is a coincidence and the two may diverge in the future.

    if isinstance(start, Iterable):
        starts = start
        for raw_encoded_chunk, start in zip(raw_encoded_chunk_stream, starts):
            end = start + len(raw_encoded_chunk)
            yield EncodedChunk(raw_encoded_chunk, start, end, encoding)
    else:
        for raw_encoded_chunk in raw_encoded_chunk_stream:
            end = start + len(raw_encoded_chunk)
            yield EncodedChunk(raw_encoded_chunk, start, end, encoding)
            start = end


def wrap_raw_decoded_chunk_stream(raw_decoded_chunk_stream: RawDecodedChunkStream, encoding: str, start: Union[int, Iterable[int]] = 0) -> DecodedChunkStream:
    """Wrap a stream of raw decoded chunks into a stream of decoded chunks.

    Args:
        raw_decoded_chunk_stream: A stream of raw decoded chunks.
        encoding: The encoding of the chunks.
        start: The start index of the first chunk in the original bytes or a stream of start indices, one for each chunk.
    """

    if isinstance(start, Iterable):
        starts = start
        for raw_decoded_chunk, start in zip(raw_decoded_chunk_stream, starts):
            end = start + len(raw_decoded_chunk.encode(encoding))
            yield DecodedChunk(raw_decoded_chunk, start, end, encoding)
    else:
        for raw_decoded_chunk in raw_decoded_chunk_stream:
            end = start + len(raw_decoded_chunk.encode(encoding))
            yield DecodedChunk(raw_decoded_chunk, start, end, encoding)
            start = end


def encoded_to_decoded_chunk_stream(encoded_chunk_stream: EncodedChunkStream) -> DecodedChunkStream:
    """Decode a stream of encoded chunks into a stream of decoded chunks.

    The encoded chunks may be truncated, in which case the truncated bytes
    will be prepended to the next chunk, if it is contiguous. Otherwise, the
    truncated bytes will be discarded.

    Raises:
        UnicodeDecodeError: If the encoded chunks cannot be decoded.
    """

    truncated_bytes = b''
    start = 0

    for encoded_chunk in encoded_chunk_stream:

        encoding = encoded_chunk.encoding

        if encoding.lower() != 'utf-8':
            raise NotImplementedError(f'Only utf-8 encoding is supported.')

        if encoded_chunk.start - len(truncated_bytes) != start:
            truncated_bytes = b''
            start = encoded_chunk.start
            encoded_chunk_bytes = lstrip_continuation_bytes(encoded_chunk.bytes)
        else:
            encoded_chunk_bytes = truncated_bytes + encoded_chunk.bytes

        split = truncation_point(encoded_chunk_bytes)

        if split < len(encoded_chunk_bytes):
            truncated_bytes = encoded_chunk_bytes[split:]
            encoded_chunk_bytes = encoded_chunk_bytes[:split]
        else:
            truncated_bytes = b''

        if encoded_chunk_bytes:
            end = start + len(encoded_chunk_bytes)
            yield DecodedChunk(encoded_chunk_bytes.decode(encoding), start, end, encoding)
            start = end


def resize_decoded_chunks_in_stream_by_num_tokens(
    decoded_chunk_stream: DecodedChunkStream,
    min_tokens = MIN_TOKENS_PER_CHUNK_DEFAULT,
    max_tokens = MAX_TOKENS_PER_CHUNK_DEFAULT,
) -> DecodedChunkStream:
    """Resize a stream of decoded chunks to be between a minimum and maximum number of tokens.
    
    The chunks will be resized to be between the minimum and maximum number of tokens,
    inclusive. If the chunk is too long, it will be split at the last preferred delimiter
    before the maximum number of tokens. If the chunk is too short, it will be appended
    to the next chunk, if it is contiguous. Otherwise, it will be discarded.
    """

    leftover_tokens = []
    start = 0

    for original_chunk in decoded_chunk_stream:

        if original_chunk.start - len(tokenizer.decode(leftover_tokens).encode(original_chunk.encoding)) != start:
            leftover_tokens = []
            start = original_chunk.start

        tokens = leftover_tokens + tokenizer.encode(original_chunk.text, disallowed_special=())

        if len(tokens) < min_tokens:
            leftover_tokens = tokens
            continue

        while len(tokens) >= min_tokens:
            resized_chunk_tokens = tokens[:max_tokens]
            resized_chunk_text = tokenizer.decode(resized_chunk_tokens)
            tokens = tokens[len(resized_chunk_tokens):]

            preferred_delimiter_index = rindex(resized_chunk_text, PREFERRED_CHUNK_DELIMITERS)

            if preferred_delimiter_index >= 0:
                resized_chunk_to_delimiter = resized_chunk_text[:preferred_delimiter_index + 1]
                tokens_to_delimiter = len(tokenizer.encode(resized_chunk_to_delimiter, disallowed_special=()))
                if tokens_to_delimiter >= min_tokens:
                    resized_chunk_after_delimiter = resized_chunk_text[preferred_delimiter_index + 1:]
                    resized_chunk_text = resized_chunk_to_delimiter
                    # Re-encode the remainder of the chunk instead of using
                    # a slice of resized_chunk_tokens, since the subset encoding
                    # (used by tokens_to_delimiter) cannot be compared to the
                    # original encoding (used by resized_chunk_tokens).
                    tokens = tokenizer.encode(resized_chunk_after_delimiter, disallowed_special=()) + tokens

            end = start + len(resized_chunk_text.encode(original_chunk.encoding))
            yield DecodedChunk(resized_chunk_text, start, end, original_chunk.encoding)
            start = end

        leftover_tokens = tokens
