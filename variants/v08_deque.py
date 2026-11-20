"""Treat the body as a queue of bytes."""

from collections import deque

MAGIC = b"fuzz"


def decode(data):
    if data[:4] != MAGIC:
        raise ValueError("missing 'fuzz' header")

    q = deque(data[4:])
    out = []
    while q:
        n = q.popleft()
        if n == 0:
            return out
        if n > len(q):
            raise ValueError("truncated chunk")
        out.append(bytes(q.popleft() for _ in range(n)).decode("utf-8"))
    raise ValueError("missing end marker")
