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
