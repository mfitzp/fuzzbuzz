"""Uses struct.unpack_from for length tokens and payloads."""

import struct

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    offset = 4
    out = []
    while True:
        (length,) = struct.unpack_from("B", data, offset)
        offset += 1
        if not length:
            break
        (raw,) = struct.unpack_from(f"{length}s", data, offset)
        out.append(raw.decode("utf-8"))
        offset += length
    return out
