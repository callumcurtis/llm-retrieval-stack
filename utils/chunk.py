import abc
import itertools
from typing import Iterable
from typing import Union

import tiktoken

from .utf8 import truncation_point
from .utf8 import lstrip_continuation_bytes
from .sequence import index_any


TOKEN_ENCODING = 'cl100k_base'
PREFERRED_CHUNK_DELIMITERS_DEFAULT = '.!?\n'
MIN_TOKENS_PER_CHUNK_DEFAULT = 50
MAX_TOKENS_PER_CHUNK_DEFAULT = 200
WORD_DELIMITERS_DEFAULT = ' .,;:!?-—\t\n\r\f\v'

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

    @property
    @abc.abstractmethod
    def encoding(self) -> str:
        pass

    @abc.abstractmethod
    def append(self, stream: Iterable[DecodedChunk]) -> '_DecodedChunkStreamInterface':
        pass

    @abc.abstractmethod
    def append_wrapped(
        self,
        raw_stream: '_DecodedChunkStreamInterface',
        start: Union[int, Iterable[int]] = 0,
    ) -> '_DecodedChunkStreamInterface':
        pass


class DecodedChunkStream(_DecodedChunkStreamInterface):
    """A stream of decoded chunks.

    Attributes:
        encoding: The encoding of the chunks. All chunks in the stream must have the same encoding.
    """

    def __init__(self, encoding: str):
        self._stream = []
        self._encoding = encoding

    def __iter__(self):
        return iter(self._stream)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._stream!r})'

    @property
    def encoding(self) -> str:
        return self._encoding

    def append(self, stream: Iterable[DecodedChunk]) -> 'DecodedChunkStream':
        """Append a stream of decoded chunks to the end of this stream."""
        self._stream = itertools.chain(self._stream, stream)
        return self

    def append_wrapped(
        self,
        raw_stream: RawDecodedChunkStream,
        start: Union[int, Iterable[int]] = 0,
    ) -> 'DecodedChunkStream':
        """Convert a stream of raw decoded chunks to a stream of decoded chunks and append it.

        Args:
            raw_stream: The stream of raw decoded chunks.
            start: The start index of the first chunk in the original bytes.
        """
        return self.append(self._wrap(raw_stream, start))

    def _wrap(
        self,
        raw_stream: RawDecodedChunkStream,
        start: Union[int, Iterable[int]] = 0,
    ) -> Iterable[DecodedChunk]:
        if isinstance(start, Iterable):
            starts = start
            for raw_decoded_chunk, start in zip(raw_stream, starts):
                end = start + len(raw_decoded_chunk.encode(self._encoding))
                yield DecodedChunk(raw_decoded_chunk, start, end, self._encoding)
        else:
            for raw_decoded_chunk in raw_stream:
                end = start + len(raw_decoded_chunk.encode(self._encoding))
                yield DecodedChunk(raw_decoded_chunk, start, end, self._encoding)
                start = end


class DecodedChunkStreamTransformer(_DecodedChunkStreamInterface, abc.ABC):
    """Decorates a decoded chunk stream to transform it."""

    def __init__(self, stream: _DecodedChunkStreamInterface):
        self._decoratee = stream

    def __iter__(self):
        return self._transformed_iter()

    def __repr__(self):
        return f'{self.__class__.__name__}({self._decoratee!r})'

    @property
    def encoding(self) -> str:
        return self._decoratee.encoding

    def append(self, stream: Iterable[DecodedChunk]) -> _DecodedChunkStreamInterface:
        self._decoratee.append(stream)
        return self

    def append_wrapped(
        self,
        raw_stream: _DecodedChunkStreamInterface,
        start: Union[int, Iterable[int]] = 0,
    ) -> _DecodedChunkStreamInterface:
        self._decoratee.append_wrapped(raw_stream, start)
        return self

    @abc.abstractmethod
    def _transformed_iter(self) -> Iterable[DecodedChunk]:
        pass


class DecodedChunkStreamSplitWordHealer(DecodedChunkStreamTransformer):
    """Heals a decoded chunk stream by moving words split across chunks to the next chunk."""

    def __init__(
        self,
        stream: _DecodedChunkStreamInterface,
        word_delimiters: str = WORD_DELIMITERS_DEFAULT,
    ):
        """
        Args:
            stream: The stream to heal.
            word_delimiters: The characters that delimit words.
        """
        super().__init__(stream)
        self._word_delimiters = word_delimiters

    def _transformed_iter(self) -> Iterable[DecodedChunk]:
        """Repair words split across chunks by moving them entirely to the next chunk.
        
        If the split cannot be healed due to a missing or noncontiguous chunk, the split is discarded.
        """

        prefix = ''
        start = 0

        for chunk in self._decoratee:

            is_contiguous_with_previous_chunk = chunk.start - len(prefix.encode(self._decoratee.encoding)) == start

            if not is_contiguous_with_previous_chunk:
                prefix = ''
                start = chunk.start

            chunk_text = prefix + chunk.text
            last_word_delimiter = index_any(chunk_text, set(self._word_delimiters), reverse=True)
            missing_prefix = not is_contiguous_with_previous_chunk and start > 0

            if missing_prefix:
                first_word_delimiter = index_any(chunk_text, set(self._word_delimiters))

            prefix = ''
            end = chunk.end

            if last_word_delimiter != -1:
                prefix = chunk_text[last_word_delimiter + 1:]
                end = chunk.end - len(prefix.encode(self._decoratee.encoding))
                chunk_text = chunk_text[:last_word_delimiter + 1]

            if missing_prefix and first_word_delimiter > 0:
                start = chunk.start + first_word_delimiter
                chunk_text = chunk_text[first_word_delimiter:]

            if chunk_text and not chunk_text.isspace():
                yield DecodedChunk(chunk_text, start, end, self._decoratee.encoding)

            start = end


class DecodedChunkStreamResizerByNumTokens(DecodedChunkStreamTransformer):
    """Resizes a decoded chunk stream to be between a minimum and maximum number of tokens."""

    def __init__(
        self,
        stream: _DecodedChunkStreamInterface,
        min_tokens_per_chunk: int = MIN_TOKENS_PER_CHUNK_DEFAULT,
        max_tokens_per_chunk: int = MAX_TOKENS_PER_CHUNK_DEFAULT,
        preferred_delimiters: Iterable[str] = PREFERRED_CHUNK_DELIMITERS_DEFAULT,
    ):
        """
        Args:
            stream: The stream to resize.
            min_tokens_per_chunk: The minimum number of tokens per chunk.
            max_tokens_per_chunk: The maximum number of tokens per chunk.
            preferred_delimiters: The preferred delimiters to split chunks at.
        """
        super().__init__(stream)
        self._min_tokens_per_chunk = min_tokens_per_chunk
        self._max_tokens_per_chunk = max_tokens_per_chunk
        self._preferred_delimiters = preferred_delimiters
    
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

            if original_chunk.start - len(tokenizer.decode(leftover_tokens).encode(self._decoratee.encoding)) != start:
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

                preferred_delimiter_index = index_any(resized_chunk_text, self._preferred_delimiters, reverse=True)

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

                end = start + len(resized_chunk_text.encode(self._decoratee.encoding))
                yield DecodedChunk(resized_chunk_text, start, end, self._decoratee.encoding)
                start = end

            leftover_tokens = tokens


class EncodedChunk:
    """An encoded chunk of bytes.

    Attributes:
        data: The encoded bytes.
        start: The start index of the chunk in the original bytes.
        end: The end index of the chunk in the original bytes.
        encoding: The encoding of the bytes.
    """

    def __init__(self, data: bytes, start: int, end: int, encoding: str):
        self._data = data
        self._start = start
        self._end = end
        self._encoding = encoding

    @property
    def data(self) -> bytes:
        return self._data

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
        return self.data == other.data and self.start == other.start and self.end == other.end

    def __repr__(self):
        return f'{self.__class__.__name__}({self.data!r}, {self.start!r}, {self.end!r}, {self.encoding!r})'


class EncodedToDecodedChunkStreamConverter(abc.ABC):

    @abc.abstractmethod
    def decode(self, encoded_chunk_stream: 'EncodedChunkStream') -> DecodedChunkStream:
        """Decode a stream of encoded chunks into a stream of decoded chunks.

        Raises:
            UnicodeDecodeError: If the encoded chunks cannot be decoded.
        """
        pass


class EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing(EncodedToDecodedChunkStreamConverter):

    def decode(self, encoded_chunk_stream: 'EncodedChunkStream') -> DecodedChunkStream:
        """Decode a stream of encoded chunks into a stream of decoded chunks.

        The encoded chunks may be split in the middle of a character. This method will
        attempt to heal the split by prepending the split bytes to the next chunk, if
        the next chunk is contiguous. Otherwise, the split bytes will be discarded.

        Raises:
            UnicodeDecodeError: If the encoded chunks cannot be decoded.
        """

        if encoded_chunk_stream.encoding.lower() != 'utf-8':
            raise NotImplementedError(f'Only utf-8 encoding is supported.')

        def converted_stream() -> Iterable[DecodedChunk]:
            truncated_bytes = b''
            start = 0

            for encoded_chunk in encoded_chunk_stream:

                if encoded_chunk.start - len(truncated_bytes) != start:
                    truncated_bytes = b''
                    start = encoded_chunk.start
                    encoded_chunk_bytes = lstrip_continuation_bytes(encoded_chunk.data)
                else:
                    encoded_chunk_bytes = truncated_bytes + encoded_chunk.data

                split = truncation_point(encoded_chunk_bytes)

                if split < len(encoded_chunk_bytes):
                    truncated_bytes = encoded_chunk_bytes[split:]
                    encoded_chunk_bytes = encoded_chunk_bytes[:split]
                else:
                    truncated_bytes = b''

                if encoded_chunk_bytes:
                    end = start + len(encoded_chunk_bytes)
                    yield DecodedChunk(encoded_chunk_bytes.decode(encoded_chunk_stream.encoding), start, end, encoded_chunk_stream.encoding)
                    start = end

        return DecodedChunkStream(encoded_chunk_stream.encoding).append(converted_stream())


RawEncodedChunkStream = Iterable[bytes]


class EncodedChunkStream(Iterable[EncodedChunk]):
    """A stream of encoded chunks.
    
    Attributes:
        encoding: The encoding of the chunks. All chunks in the stream must have the same encoding.
    """

    def __init__(
        self,
        encoding: str,
        decoder: EncodedToDecodedChunkStreamConverter = EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing(),
    ):
        """
        Args:
            encoding: The encoding of the chunks. All chunks in the stream must have the same encoding.
            decoder: The decoder to use to decode the encoded chunks.
        """
        self._stream = []
        self._encoding = encoding
        self._decoder = decoder

    def __iter__(self):
        return iter(self._stream)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._stream!r})'

    @property
    def encoding(self) -> str:
        return self._encoding

    def append(self, stream: Iterable[EncodedChunk]) -> 'EncodedChunkStream':
        """Append a stream of encoded chunks to the end of the stream."""
        self._stream = itertools.chain(self._stream, stream)
        return self

    def append_wrapped(
        self,
        raw_stream: RawEncodedChunkStream,
        start: Union[int, Iterable[int]] = 0,
    ) -> 'EncodedChunkStream':
        """Convert a stream of raw encoded chunks into a stream of encoded chunks and append it.
        
        Args:
            raw_stream: A stream of raw encoded chunks.
            start: The start index of the first chunk in the original bytes or a stream of start indices, one for each chunk.
        """
        return self.append(self._wrap(raw_stream, start))

    def _wrap(
        self,
        raw_stream: RawEncodedChunkStream,
        start: Union[int, Iterable[int]] = 0,
    ) -> Iterable[EncodedChunk]:
        if isinstance(start, Iterable):
            starts = start
            for raw_encoded_chunk, start in zip(raw_stream, starts):
                end = start + len(raw_encoded_chunk)
                yield EncodedChunk(raw_encoded_chunk, start, end, self._encoding)
        else:
            for raw_encoded_chunk in raw_stream:
                end = start + len(raw_encoded_chunk)
                yield EncodedChunk(raw_encoded_chunk, start, end, self._encoding)
                start = end

    def decode(self) -> DecodedChunkStream:
        return self._decoder.decode(self)
