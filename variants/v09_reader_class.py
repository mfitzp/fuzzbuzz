"""Small cursor class with read/read_byte helpers."""

MAGIC = b"fuzz"


class _Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self, n):
        chunk = self.data[self.pos : self.pos + n]
        if len(chunk) != n:
            raise EOFError(f"wanted {n} bytes at offset {self.pos}")
        self.pos += n
        return chunk

    def read_byte(self):
        return self.read(1)[0]


def decode(data):
    reader = _Reader(data)
    try:
        magic = reader.read(len(MAGIC))
    except EOFError:
        raise ValueError("missing 'fuzz' header") from None
    if magic != MAGIC:
        raise ValueError("missing 'fuzz' header")

    chunks = []
    while (length := reader.read_byte()) != 0:
        chunks.append(reader.read(length).decode("utf-8"))
    return chunks
