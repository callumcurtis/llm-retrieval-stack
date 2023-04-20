from typing import Iterator

from .utf8 import truncation_point


ENCODED_CHUNK_STREAM = Iterator[bytes]
DECODED_CHUNK_STREAM = Iterator[str]

ENCODING = 'UTF-8'


def decoded_chunk_stream(encoded_chunk_stream: ENCODED_CHUNK_STREAM) -> DECODED_CHUNK_STREAM:
    """Decode a stream of encoded chunks into a stream of decoded chunks.

    The encoded chunks may be truncated, in which case the truncated bytes
    will be prepended to the next chunk.
    
    Raises:
        UnicodeDecodeError: If the encoded chunks are not valid UTF-8.
    """

    truncated_bytes = b''

    for encoded_chunk in encoded_chunk_stream:
        encoded_chunk = truncated_bytes + encoded_chunk
        split = truncation_point(encoded_chunk)

        if split < len(encoded_chunk):
            truncated_bytes = encoded_chunk[split:]
            encoded_chunk = encoded_chunk[:split]
        else:
            truncated_bytes = b''

        if encoded_chunk:
            yield encoded_chunk.decode(ENCODING)
