from typing import Iterator

import tiktoken

from .utf8 import truncation_point
from .sequence import rindex


ENCODED_CHUNK_STREAM = Iterator[bytes]
DECODED_CHUNK_STREAM = Iterator[str]

CHARACTER_ENCODING_DEFAULT = 'utf-8'
TOKEN_ENCODING = 'cl100k_base'
PREFERRED_CHUNK_DELIMITERS = '.!?\n'

tokenizer = tiktoken.get_encoding(TOKEN_ENCODING)


def decoded_chunk_stream(encoded_chunk_stream: ENCODED_CHUNK_STREAM, encoding = CHARACTER_ENCODING_DEFAULT) -> DECODED_CHUNK_STREAM:
    """Decode a stream of encoded chunks into a stream of decoded chunks.

    The encoded chunks may be truncated, in which case the truncated bytes
    will be prepended to the next chunk.
    
    Raises:
        UnicodeDecodeError: If the encoded chunks cannot be decoded.
    """

    if encoding.lower() != CHARACTER_ENCODING_DEFAULT.lower():
        raise NotImplementedError(f'Only {CHARACTER_ENCODING_DEFAULT} encoding is supported.')

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
            yield encoded_chunk.decode(CHARACTER_ENCODING_DEFAULT)


def resize_by_num_tokens(
    decoded_chunk_stream: DECODED_CHUNK_STREAM,
    min_tokens: int,
    max_tokens: int,
) -> DECODED_CHUNK_STREAM:
    """Resize a stream of decoded chunks to be between a minimum and maximum number of tokens."""

    leftover_tokens = []

    for original_chunk in decoded_chunk_stream:

        tokens = leftover_tokens + tokenizer.encode(original_chunk, disallowed_special=())

        if len(tokens) < min_tokens:
            leftover_tokens = tokens
            continue

        while len(tokens) >= min_tokens:
            resized_chunk_tokens = tokens[:max_tokens]
            resized_chunk = tokenizer.decode(resized_chunk_tokens)
            tokens = tokens[len(resized_chunk_tokens):]

            preferred_delimiter_index = rindex(resized_chunk, PREFERRED_CHUNK_DELIMITERS)

            if preferred_delimiter_index >= 0:
                resized_chunk_to_delimiter = resized_chunk[:preferred_delimiter_index + 1]
                tokens_to_delimiter = len(tokenizer.encode(resized_chunk_to_delimiter, disallowed_special=()))
                if tokens_to_delimiter >= min_tokens:
                    resized_chunk_after_delimiter = resized_chunk[preferred_delimiter_index + 1:]
                    resized_chunk = resized_chunk_to_delimiter
                    # Re-encode the remainder of the chunk instead of using
                    # a slice of resized_chunk_tokens, since the subset encoding
                    # (used by tokens_to_delimiter) cannot be compared to the
                    # original encoding (used by resized_chunk_tokens).
                    tokens = tokenizer.encode(resized_chunk_after_delimiter, disallowed_special=()) + tokens

            yield resized_chunk

        leftover_tokens = tokens
