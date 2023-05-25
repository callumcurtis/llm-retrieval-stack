import abc
import itertools
from typing import Iterable
from typing import Union

from llm_retrieval.document.chunk import DecodedChunk


RawDecodedChunkStream = Iterable[str]


class DecodedChunkStreamInterface(Iterable[DecodedChunk], abc.ABC):

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
    def append(self, stream: Iterable[DecodedChunk]) -> 'DecodedChunkStreamInterface':
        pass

    @abc.abstractmethod
    def append_wrapped(
        self,
        raw_stream: 'DecodedChunkStreamInterface',
        start: Union[int, Iterable[int]] = 0,
    ) -> 'DecodedChunkStreamInterface':
        pass


class DecodedChunkStream(DecodedChunkStreamInterface):
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
            for raw_decoded_chunk, start in itertools.zip_longest(raw_stream, starts):
                if start is None or raw_decoded_chunk is None:
                    raise ValueError('raw_stream and start must be the same length')
                end = start + len(raw_decoded_chunk.encode(self._encoding))
                yield DecodedChunk(raw_decoded_chunk, start, end, self._encoding)
        else:
            for raw_decoded_chunk in raw_stream:
                end = start + len(raw_decoded_chunk.encode(self._encoding))
                yield DecodedChunk(raw_decoded_chunk, start, end, self._encoding)
                start = end
