"""Byte-at-a-time state machine."""

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    chunks = []
    current = bytearray()
    remaining = 0
    for byte in data[4:]:
        if remaining:
            current.append(byte)
            remaining -= 1
            if not remaining:
                chunks.append(current.decode("utf-8"))
                current = bytearray()
        elif byte == 0:
            return chunks
        else:
            remaining = byte
    raise ValueError("unexpected end of stream")
