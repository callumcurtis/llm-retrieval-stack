import itertools
from typing import Iterable
from typing import Union

from llm_retrieval.document.chunk import EncodedChunk


RawEncodedChunkStream = Iterable[bytes]


class EncodedChunkStream(Iterable[EncodedChunk]):
    """A stream of encoded chunks.
    
    Attributes:
        encoding: The encoding of the chunks. All chunks in the stream must have the same encoding.
    """

    def __init__(self, encoding: str):
        """
        Args:
            encoding: The encoding of the chunks. All chunks in the stream must have the same encoding.
        """
        self._stream = []
        self._encoding = encoding

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
            for raw_encoded_chunk, start in itertools.zip_longest(raw_stream, starts):
                if start is None or raw_encoded_chunk is None:
                    raise ValueError('raw_stream and start must be the same length')
                end = start + len(raw_encoded_chunk)
                yield EncodedChunk(raw_encoded_chunk, start, end, self._encoding)
        else:
            for raw_encoded_chunk in raw_stream:
                end = start + len(raw_encoded_chunk)
                yield EncodedChunk(raw_encoded_chunk, start, end, self._encoding)
                start = end
