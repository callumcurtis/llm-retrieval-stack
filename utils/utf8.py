MAX_UTF8_BYTES_PER_CHAR = 4
MAX_UTF8_CONTINUATION_BYTES_PER_CHAR = MAX_UTF8_BYTES_PER_CHAR - 1

UTF8_START_BYTE_MASK_AND_VALUE_BY_LENGTH = {
    1: (0b10000000, 0b00000000),
    2: (0b11100000, 0b11000000),
    3: (0b11110000, 0b11100000),
    4: (0b11111000, 0b11110000),
}

UTF8_CONTINUATION_BYTE_MASK = 0b11000000
UTF8_CONTINUATION_BYTE_VALUE = 0b10000000


def truncation_point(data: bytes) -> int:
    """Find the point at which a UTF-8 binary string has been truncated."""

    num_continuation_bytes = 0
    for byte in reversed(data):
        if byte & UTF8_CONTINUATION_BYTE_MASK == UTF8_CONTINUATION_BYTE_VALUE:
            num_continuation_bytes += 1
        else:
            break
        if num_continuation_bytes >= MAX_UTF8_CONTINUATION_BYTES_PER_CHAR:
            break

    if num_continuation_bytes == len(data):
        return 0

    start_byte_pos = len(data) - num_continuation_bytes - 1
    start_byte = data[start_byte_pos]    
    start_byte_mask, expected_start_byte_value = UTF8_START_BYTE_MASK_AND_VALUE_BY_LENGTH[num_continuation_bytes + 1]

    if start_byte & start_byte_mask == expected_start_byte_value:
        return len(data)

    return start_byte_pos
