import abc
import itertools
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
        return f'{self.__class__.__name__}({self.text!r}, {self.start!r}, {self.end!r}, {self.encoding!r})'


RawDecodedChunkStream = Iterable[str]


class _DecodedChunkStreamInterface(Iterable[DecodedChunk], abc.ABC):

    @abc.abstractmethod
    def __iter__(self):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def append(self, stream: Iterable[DecodedChunk]) -> '_DecodedChunkStreamInterface':
        pass

    @abc.abstractmethod
    def append_wrapped(
        self,
        raw_stream: '_DecodedChunkStreamInterface',
        encoding: str,
        start: Union[int, Iterable[int]] = 0,
    ) -> '_DecodedChunkStreamInterface':
        pass


class DecodedChunkStream(_DecodedChunkStreamInterface):
    """A stream of decoded chunks."""

    def __init__(self):
        self._stream = []

    def __iter__(self):
        return iter(self._stream)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._stream!r})'

    def append(self, stream: Iterable[DecodedChunk]) -> 'DecodedChunkStream':
        """Append a stream of decoded chunks to the end of this stream."""
        self._stream = itertools.chain(self._stream, stream)
        return self

    def append_wrapped(
        self,
        raw_stream: RawDecodedChunkStream,
        encoding: str,
        start: Union[int, Iterable[int]] = 0,
    ) -> 'DecodedChunkStream':
        """Convert a stream of raw decoded chunks to a stream of decoded chunks and append it.

        Args:
            raw_stream: The stream of raw decoded chunks.
            encoding: The encoding of the raw decoded chunks.
            start: The start index of the first chunk in the original bytes.
        """
        return self.append(self._wrap(raw_stream, encoding, start))

    def _wrap(
        self,
        raw_stream: RawDecodedChunkStream,
        encoding: str,
        start: Union[int, Iterable[int]] = 0,
    ) -> Iterable[DecodedChunk]:
        if isinstance(start, Iterable):
            starts = start
            for raw_decoded_chunk, start in zip(raw_stream, starts):
                end = start + len(raw_decoded_chunk.encode(encoding))
                yield DecodedChunk(raw_decoded_chunk, start, end, encoding)
        else:
            for raw_decoded_chunk in raw_stream:
                end = start + len(raw_decoded_chunk.encode(encoding))
                yield DecodedChunk(raw_decoded_chunk, start, end, encoding)
                start = end


class DecodedChunkStreamTransformer(_DecodedChunkStreamInterface, abc.ABC):
    """Decorates a decoded chunk stream to transform it."""

    def __init__(self, stream: _DecodedChunkStreamInterface):
        self._decoratee = stream

    def __iter__(self):
        return self._transformed_iter()

    def __repr__(self):
        return f'{self.__class__.__name__}({self._decoratee!r})'

    def append(self, stream: Iterable[DecodedChunk]) -> _DecodedChunkStreamInterface:
        self._decoratee.append(stream)
        return self

    def append_wrapped(
        self,
        raw_stream: _DecodedChunkStreamInterface,
        encoding: str,
        start: Union[int, Iterable[int]] = 0,
    ) -> _DecodedChunkStreamInterface:
        self._decoratee.append_wrapped(raw_stream, encoding, start)
        return self

    @abc.abstractmethod
    def _transformed_iter(self) -> Iterable[DecodedChunk]:
        raise NotImplementedError


class DecodedChunkStreamResizerByNumTokens(DecodedChunkStreamTransformer):
    """Resizes a decoded chunk stream to be between a minimum and maximum number of tokens."""

    def __init__(
        self,
        stream: _DecodedChunkStreamInterface,
        min_tokens_per_chunk: int = MIN_TOKENS_PER_CHUNK_DEFAULT,
        max_tokens_per_chunk: int = MAX_TOKENS_PER_CHUNK_DEFAULT,
    ):
        """
        Args:
            stream: The stream to resize.
            min_tokens_per_chunk: The minimum number of tokens per chunk.
            max_tokens_per_chunk: The maximum number of tokens per chunk.
        """
        super().__init__(stream)
        self._min_tokens_per_chunk = min_tokens_per_chunk
        self._max_tokens_per_chunk = max_tokens_per_chunk
    
    def _transformed_iter(self) -> Iterable[DecodedChunk]:
        """Resize the stream to be between a minimum and maximum number of tokens.

        The chunks will be resized to be between the minimum and maximum number of tokens,
        inclusive. If the chunk is too long, it will be split at the last preferred delimiter
        before the maximum number of tokens. If the chunk is too short, it will be appended
        to the next chunk, if it is contiguous. Otherwise, it will be discarded.
        """

        leftover_tokens = []
        start = 0

        for original_chunk in self._decoratee:

            if original_chunk.start - len(tokenizer.decode(leftover_tokens).encode(original_chunk.encoding)) != start:
                leftover_tokens = []
                start = original_chunk.start

            tokens = leftover_tokens + tokenizer.encode(original_chunk.text, disallowed_special=())

            if len(tokens) < self._min_tokens_per_chunk:
                leftover_tokens = tokens
                continue

            while len(tokens) >= self._min_tokens_per_chunk:
                resized_chunk_tokens = tokens[:self._max_tokens_per_chunk]
                resized_chunk_text = tokenizer.decode(resized_chunk_tokens)
                tokens = tokens[len(resized_chunk_tokens):]

                preferred_delimiter_index = rindex(resized_chunk_text, PREFERRED_CHUNK_DELIMITERS)

                if preferred_delimiter_index >= 0:
                    resized_chunk_to_delimiter = resized_chunk_text[:preferred_delimiter_index + 1]
                    tokens_to_delimiter = len(tokenizer.encode(resized_chunk_to_delimiter, disallowed_special=()))
                    if tokens_to_delimiter >= self._min_tokens_per_chunk:
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
        return f'{self.__class__.__name__}({self.bytes!r}, {self.start!r}, {self.end!r}, {self.encoding!r})'


class EncodedToDecodedChunkStreamConverter(abc.ABC):

    @abc.abstractmethod
    def decode(self, encoded_chunk_stream: 'EncodedChunkStream') -> DecodedChunkStream:
        """Decode a stream of encoded chunks into a stream of decoded chunks.

        Raises:
            UnicodeDecodeError: If the encoded chunks cannot be decoded.
        """
        raise NotImplementedError


class EncodedToDecodedChunkStreamConverterWithTruncationHealing(EncodedToDecodedChunkStreamConverter):

    def decode(self, encoded_chunk_stream: 'EncodedChunkStream') -> DecodedChunkStream:
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


RawEncodedChunkStream = Iterable[bytes]


class EncodedChunkStream(Iterable[EncodedChunk]):
    """A stream of encoded chunks."""

    def __init__(
        self,
        decoder = EncodedToDecodedChunkStreamConverterWithTruncationHealing(),
    ):
        """
        Args:
            decoder: The decoder to use to decode the encoded chunks.
        """
        self._stream = []
        self._decoder = decoder

    def __iter__(self):
        return iter(self._stream)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._stream!r})'

    def append(self, stream: Iterable[EncodedChunk]) -> 'EncodedChunkStream':
        """Append a stream of encoded chunks to the end of the stream."""
        self._stream = itertools.chain(self._stream, stream)
        return self

    def append_wrapped(
        self,
        raw_stream: RawEncodedChunkStream,
        encoding: str,
        start: Union[int, Iterable[int]] = 0,
    ) -> 'EncodedChunkStream':
        """Convert a stream of raw encoded chunks into a stream of encoded chunks and append it.
        
        Args:
            raw_stream: A stream of raw encoded chunks.
            encoding: The encoding of the chunks.
            start: The start index of the first chunk in the original bytes or a stream of start indices, one for each chunk.
        """
        return self.append(self._wrap(raw_stream, encoding, start))

    def _wrap(
        self,
        raw_stream: RawEncodedChunkStream,
        encoding: str,
        start: Union[int, Iterable[int]] = 0,
    ) -> Iterable[EncodedChunk]:
        if isinstance(start, Iterable):
            starts = start
            for raw_encoded_chunk, start in zip(raw_stream, starts):
                end = start + len(raw_encoded_chunk)
                yield EncodedChunk(raw_encoded_chunk, start, end, encoding)
        else:
            for raw_encoded_chunk in raw_stream:
                end = start + len(raw_encoded_chunk)
                yield EncodedChunk(raw_encoded_chunk, start, end, encoding)
                start = end

    def decode(self) -> DecodedChunkStream:
        return self._decoder.decode(self)
