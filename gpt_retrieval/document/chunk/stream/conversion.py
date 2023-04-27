import abc
from typing import Iterable

from . import EncodedChunkStream
from . import DecodedChunkStream
from gpt_retrieval.document.chunk import DecodedChunk
from gpt_retrieval.utils.common.utf8 import lstrip_continuation_bytes
from gpt_retrieval.utils.common.utf8 import truncation_point


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
