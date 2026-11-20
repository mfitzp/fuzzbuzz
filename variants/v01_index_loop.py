"""Index-based loop with explicit bounds checks."""

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    out = []
    i = 4
    n = len(data)
    while i < n:
        length = data[i]
        i += 1
        if length == 0:
            return out
        end = i + length
        if end > n:
            raise ValueError("truncated chunk")
        out.append(data[i:end].decode("utf-8"))
        i = end
    raise ValueError("missing end marker")
