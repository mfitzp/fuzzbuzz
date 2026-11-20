"""Stream-style reader over io.BytesIO."""

import io

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    stream = io.BytesIO(data)
    stream.seek(len(MAGIC))
    chunks = []
    while True:
        token = stream.read(1)
        if not token:
            raise EOFError("unexpected end of stream")
        (length,) = token
        if length == 0:
            return chunks
        payload = stream.read(length)
        if len(payload) != length:
            raise EOFError("truncated chunk")
        chunks.append(payload.decode())
