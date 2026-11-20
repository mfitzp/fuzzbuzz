"""Generator yields raw chunks; decode() turns them into strings."""

MAGIC = b"fuzz"


def _iter_chunks(data, pos):
    while pos < len(data):
        length = data[pos]
        if length == 0:
            return
        yield data[pos + 1 : pos + 1 + length]
        pos += 1 + length
    raise ValueError("stream ended without end marker")


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")
    return [chunk.decode("utf-8") for chunk in _iter_chunks(data, 4)]
