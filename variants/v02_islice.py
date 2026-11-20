"""Consume a single byte iterator, using islice to pull each chunk."""

from itertools import islice

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    it = iter(data[4:])
    result = []
    for length in it:
        if length == 0:
            break
        result.append(bytes(islice(it, length)).decode("utf-8"))
    return result
