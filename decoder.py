"""A deliberately simple (and deliberately buggy) decoder for the "fuzz" format.

Format
------
    b"fuzz"                    4-byte magic header
    <len> <len bytes of utf-8>  a chunk; <len> is a single byte, 1-255
    <len> <len bytes of utf-8>  ... repeated any number of times
    0x00                       end marker (a zero length token)

Anything after the end marker is ignored.

Known bug (intentional): the decoder never checks that it is still inside
the buffer before reading a length token. A stream that runs out before the
end marker (missing terminator, truncated chunk, ...) reads past the end of
the data and crashes with IndexError.
"""

MAGIC = b"fuzz"
END_MARKER = 0


def decode(data: bytes) -> list[str]:
    if data[: len(MAGIC)] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    pos = len(MAGIC)
    chunks = []

    while True:
        length = data[pos]  # BUG: no bounds check on reading the length token
        pos += 1

        if length == END_MARKER:
            break

        chunks.append(data[pos : pos + length].decode("utf-8"))
        pos += length

    return chunks
