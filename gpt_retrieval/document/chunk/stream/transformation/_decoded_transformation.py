import abc
import itertools
from typing import Iterable
from typing import Union

import tiktoken

from gpt_retrieval.document.chunk import DecodedChunk
from gpt_retrieval.document.chunk.stream import DecodedChunkStreamInterface
from gpt_retrieval.utils.common.sequence import index_any


TOKEN_ENCODING_DEFAULT = 'cl100k_base'
PREFERRED_CHUNK_DELIMITERS_DEFAULT = '.!?\n'
WORD_DELIMITERS_DEFAULT = ' .,;:!?-—\t\n\r\f\v'
MIN_TOKENS_PER_CHUNK_DEFAULT = 50
MAX_TOKENS_PER_CHUNK_DEFAULT = 200

tokenizer_default = tiktoken.get_encoding(TOKEN_ENCODING_DEFAULT)


class DecodedChunkStreamTransformer(DecodedChunkStreamInterface, abc.ABC):
    """Decorates a decoded chunk stream to transform it."""

    def __init__(self, stream: DecodedChunkStreamInterface):
        self._decoratee = stream

    def __iter__(self):
        return self._transformed_iter()

    def __repr__(self):
        return f'{self.__class__.__name__}({self._decoratee!r})'

    @property
    def encoding(self) -> str:
        return self._decoratee.encoding

    def append(self, stream: Iterable[DecodedChunk]) -> DecodedChunkStreamInterface:
        self._decoratee.append(stream)
        return self

    def append_wrapped(
        self,
        raw_stream: DecodedChunkStreamInterface,
        start: Union[int, Iterable[int]] = 0,
    ) -> DecodedChunkStreamInterface:
        self._decoratee.append_wrapped(raw_stream, start)
        return self

    @abc.abstractmethod
    def _transformed_iter(self) -> Iterable[DecodedChunk]:
        pass


class DecodedChunkStreamSplitWordHealer(DecodedChunkStreamTransformer):
    """Heals a decoded chunk stream by moving words split across chunks to the next chunk."""

    def __init__(
        self,
        stream: DecodedChunkStreamInterface,
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
        stream: DecodedChunkStreamInterface,
        min_tokens_per_chunk: int = MIN_TOKENS_PER_CHUNK_DEFAULT,
        max_tokens_per_chunk: int = MAX_TOKENS_PER_CHUNK_DEFAULT,
        tokenizer: tiktoken.Encoding = tokenizer_default,
        preferred_delimiters: Iterable[str] = PREFERRED_CHUNK_DELIMITERS_DEFAULT,
    ):
        """
        Args:
            stream: The stream to resize.
            min_tokens_per_chunk: The minimum number of tokens per chunk.
            max_tokens_per_chunk: The maximum number of tokens per chunk.
            tokenizer: The tokenizer to use to count tokens.
            preferred_delimiters: The preferred delimiters to split chunks at.
        """
        super().__init__(stream)
        self._min_tokens_per_chunk = min_tokens_per_chunk
        self._max_tokens_per_chunk = max_tokens_per_chunk
        self._tokenizer = tokenizer
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

            if original_chunk.start - len(self._tokenizer.decode(leftover_tokens).encode(self._decoratee.encoding)) != start:
                leftover_tokens = []
                start = original_chunk.start

            original_chunk_tokens = self._tokenizer.encode(original_chunk.text, disallowed_special=())
            tokens = itertools.chain(leftover_tokens, original_chunk_tokens)
            n_tokens = len(leftover_tokens) + len(original_chunk_tokens)

            if n_tokens < self._min_tokens_per_chunk:
                leftover_tokens = list(tokens)
                continue

            while n_tokens >= self._min_tokens_per_chunk:
                resized_chunk_tokens = list(itertools.islice(tokens, self._max_tokens_per_chunk))
                n_tokens -= len(resized_chunk_tokens)
                resized_chunk_text = self._tokenizer.decode(resized_chunk_tokens)

                preferred_delimiter_index = index_any(resized_chunk_text, self._preferred_delimiters, reverse=True)

                if preferred_delimiter_index >= 0:
                    resized_chunk_text_to_delimiter = resized_chunk_text[:preferred_delimiter_index + 1]
                    resized_chunk_tokens_to_delimiter = self._tokenizer.encode(resized_chunk_text_to_delimiter, disallowed_special=())
                    if len(resized_chunk_tokens_to_delimiter) >= self._min_tokens_per_chunk:
                        resized_chunk_text_after_delimiter = resized_chunk_text[preferred_delimiter_index + 1:]
                        resized_chunk_text = resized_chunk_text_to_delimiter
                        # Re-encode the remainder of the chunk instead of using
                        # a slice of resized_chunk_tokens, since the subset encoding
                        # (used by tokens_to_delimiter) cannot be compared to the
                        # original encoding (used by resized_chunk_tokens).
                        resized_chunk_tokens_after_delimiter = self._tokenizer.encode(resized_chunk_text_after_delimiter, disallowed_special=())
                        tokens = itertools.chain(resized_chunk_tokens_after_delimiter, tokens)
                        n_tokens += len(resized_chunk_tokens_after_delimiter)

                end = start + len(resized_chunk_text.encode(self._decoratee.encoding))
                yield DecodedChunk(resized_chunk_text, start, end, self._decoratee.encoding)
                start = end

            leftover_tokens = list(tokens)
