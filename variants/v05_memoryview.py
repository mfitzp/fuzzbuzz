"""Zero-copy consumption of a memoryview."""

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    view = memoryview(data)[4:]
    out = []
    while view:
        length = view[0]
        if length == 0:
            return out
        chunk = view[1 : 1 + length]
        if len(chunk) < length:
            raise ValueError("truncated chunk")
        out.append(str(chunk, "utf-8"))
        view = view[1 + length :]
    raise ValueError("missing end marker")
