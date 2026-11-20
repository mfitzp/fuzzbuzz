"""Strip the header, then repeatedly slice the remainder."""

MAGIC = b"fuzz"


def decode(data):
    if not isinstance(data, (bytes, bytearray)) or not data.startswith(MAGIC):
        raise ValueError("missing 'fuzz' header")

    rest = bytes(data).removeprefix(MAGIC)
    out = []
    while rest and rest[0]:
        n = rest[0]
        out.append(rest[1 : 1 + n].decode("utf-8"))
        rest = rest[1 + n :]
    if not rest:
        raise ValueError("missing end marker")
    return out
