import pytest


UTF8_CHARS = [
    b'\x00',
    b'\x7f',
    b'\xc2\x80',
    b'\xdf\xbf',
    b'\xe0\xa0\x80',
    b'\xef\xbf\xbf',
    b'\xf0\x90\x80\x80',
    b'\xf4\x8f\xbf\xbf',
]


def truncations(char):
    return (char[:i] for i in range(1, len(char)))


@pytest.fixture(params=UTF8_CHARS)
def utf8_char(request):
    return request.param


@pytest.fixture(params=(t for c in UTF8_CHARS for t in truncations(c)))
def utf8_truncation(request):
    return request.param
