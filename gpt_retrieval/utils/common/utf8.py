import itertools


MAX_UTF8_BYTES_PER_CHAR = 4
MAX_UTF8_CONTINUATION_BYTES_PER_CHAR = MAX_UTF8_BYTES_PER_CHAR - 1

UTF8_START_BYTE_MASK_AND_VALUE_BY_LENGTH = {
    1: (0b10000000, 0b00000000),
    2: (0b11100000, 0b11000000),
    3: (0b11110000, 0b11100000),
    4: (0b11111000, 0b11110000),
}


def is_continuation_byte(byte: int) -> bool:
    """Check if a byte is a UTF-8 continuation byte."""
    return byte & 0b11000000 == 0b10000000


def leading_continuation_bytes(data: bytes) -> int:
    """Count the number of UTF-8 continuation bytes at the start of a binary string."""
    return sum(1 for _ in itertools.takewhile(is_continuation_byte, data))


def truncation_point(data: bytes) -> int:
    """Find the point at which a UTF-8 binary string has been truncated."""

    num_continuation_bytes = leading_continuation_bytes(reversed(data))

    if num_continuation_bytes == len(data):
        return 0

    start_byte_pos = len(data) - num_continuation_bytes - 1
    start_byte = data[start_byte_pos]    
    start_byte_mask, expected_start_byte_value = UTF8_START_BYTE_MASK_AND_VALUE_BY_LENGTH[num_continuation_bytes + 1]

    if start_byte & start_byte_mask == expected_start_byte_value:
        return len(data)

    return start_byte_pos


def lstrip_continuation_bytes(data: bytes) -> bytes:
    """Remove leading UTF-8 continuation bytes from a binary string."""
    return data[leading_continuation_bytes(data):]


def rstrip_continuation_bytes(data: bytes) -> bytes:
    """Remove trailing UTF-8 continuation bytes from a binary string."""
    return data[:len(data) - leading_continuation_bytes(reversed(data))]


def strip_continuation_bytes(data: bytes) -> bytes:
    """Remove leading and trailing UTF-8 continuation bytes from a binary string."""
    return rstrip_continuation_bytes(lstrip_continuation_bytes(data))
