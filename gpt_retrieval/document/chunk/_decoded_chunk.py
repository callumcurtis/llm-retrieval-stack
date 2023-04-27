class DecodedChunk:
    """A decoded chunk of text.
    
    Attributes:
        text: The decoded text.
        start: The start index of the chunk in the original bytes.
        end: The end index of the chunk in the original bytes.
        encoding: The encoding of the text.
    """

    def __init__(self, text: str, start: int, end: int, encoding: str):
        self._text = text
        self._start = start
        self._end = end
        self._encoding = encoding

    @property
    def text(self) -> str:
        return self._text

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
        if not isinstance(other, DecodedChunk):
            return False
        return self.text == other.text and self.start == other.start and self.end == other.end

    def __repr__(self):
        return f'{self.__class__.__name__}({self.text!r}, {self.start!r}, {self.end!r}, {self.encoding!r})'
