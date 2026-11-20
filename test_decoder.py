"""Tests defining the known/expected behaviour of decoder.decode.

These describe the decoder *as written*. They intentionally never exercise
the out-of-bounds read: every stream passed in is well-formed enough that
the decoder reaches an end marker before running out of data.
"""

import pytest

from decoder import decode


def encode(*chunks: str) -> bytes:
    """Build a well-formed stream from the given strings."""
    out = bytearray(b"fuzz")
    for chunk in chunks:
        raw = chunk.encode("utf-8")
        assert 1 <= len(raw) <= 255
        out.append(len(raw))
        out += raw
    out.append(0)
    return bytes(out)


# --- Basic decoding -------------------------------------------------------


def test_no_chunks():
    assert decode(b"fuzz\x00") == []


def test_single_chunk():
    assert decode(b"fuzz\x05hello\x00") == ["hello"]


def test_multiple_chunks():
    assert decode(b"fuzz\x05hello\x05world\x00") == ["hello", "world"]


def test_chunk_order_is_preserved():
    words = ["one", "two", "three", "four", "five"]
    assert decode(encode(*words)) == words


def test_duplicate_chunks_are_kept():
    assert decode(encode("a", "a", "a")) == ["a", "a", "a"]


def test_returns_list_of_str():
    result = decode(encode("abc"))
    assert type(result) is list
    assert all(type(s) is str for s in result)


def test_returns_new_list_each_call():
    data = encode("x")
    assert decode(data) is not decode(data)


# --- Length tokens --------------------------------------------------------


def test_minimum_chunk_length_one():
    assert decode(b"fuzz\x01a\x00") == ["a"]


def test_maximum_chunk_length_255():
    s = "x" * 255
    data = b"fuzz\xff" + s.encode() + b"\x00"
    assert decode(data) == [s]


@pytest.mark.parametrize("n", [1, 2, 127, 128, 254, 255])
def test_various_lengths(n):
    s = "q" * n
    assert decode(encode(s)) == [s]


def test_many_max_length_chunks():
    chunks = [chr(ord("a") + i) * 255 for i in range(10)]
    assert decode(encode(*chunks)) == chunks


def test_many_small_chunks():
    chunks = [str(i % 10) for i in range(1000)]
    assert decode(encode(*chunks)) == chunks


def test_length_is_in_bytes_not_characters():
    # "é" is 2 bytes in utf-8, so length token is 2 for a 1-character string.
    assert decode(b"fuzz\x02\xc3\xa9\x00") == ["é"]


def test_chunk_content_may_contain_zero_bytes():
    # A NUL inside a chunk is data, not an end marker.
    assert decode(b"fuzz\x03a\x00b\x00") == ["a\x00b"]


def test_chunk_content_may_look_like_length_tokens():
    assert decode(b"fuzz\x02\x01\x02\x00") == ["\x01\x02"]


def test_chunk_content_may_contain_magic():
    assert decode(encode("fuzz", "fuzzfuzz")) == ["fuzz", "fuzzfuzz"]


def test_empty_strings_cannot_be_encoded():
    # A zero length token always terminates; it never yields "".
    assert decode(b"fuzz\x00\x00\x00") == []


# --- UTF-8 content --------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "ascii",
        "café",
        "日本語",
        "🐍🔥",
        "mixed é 日 🐍",
        "\t\n\r ",
        "\u0000",
        "\U0010ffff",
    ],
)
def test_utf8_round_trip(text):
    assert decode(encode(text)) == [text]


def test_multibyte_at_max_length():
    s = "日" * 85  # 85 * 3 bytes = 255
    assert len(s.encode()) == 255
    assert decode(encode(s)) == [s]


def test_invalid_utf8_raises():
    with pytest.raises(UnicodeDecodeError):
        decode(b"fuzz\x01\xff\x00")


def test_multibyte_char_split_across_chunks_raises():
    # "é" = c3 a9; splitting it over two chunks makes each invalid.
    with pytest.raises(UnicodeDecodeError):
        decode(b"fuzz\x01\xc3\x01\xa9\x00")


def test_overlong_encoding_rejected():
    # 0xc0 0x80 is an overlong encoding of NUL, invalid in strict utf-8.
    with pytest.raises(UnicodeDecodeError):
        decode(b"fuzz\x02\xc0\x80\x00")


def test_surrogate_rejected():
    # ed a0 80 encodes U+D800, a lone surrogate.
    with pytest.raises(UnicodeDecodeError):
        decode(b"fuzz\x03\xed\xa0\x80\x00")


def test_bom_is_preserved():
    assert decode(b"fuzz\x03\xef\xbb\xbf\x00") == ["﻿"]


# --- Header ---------------------------------------------------------------


def test_empty_input_raises():
    with pytest.raises(ValueError):
        decode(b"")


@pytest.mark.parametrize("data", [b"f", b"fu", b"fuz"])
def test_partial_header_raises(data):
    with pytest.raises(ValueError):
        decode(data)


@pytest.mark.parametrize(
    "data",
    [
        b"FUZZ\x00",
        b"Fuzz\x00",
        b"buzz\x00",
        b"fuz\x00",
        b"\x00fuzz\x00",
        b" fuzz\x00",
        b"zzuf\x00",
    ],
)
def test_wrong_header_raises(data):
    with pytest.raises(ValueError):
        decode(data)


def test_header_error_message():
    with pytest.raises(ValueError, match="fuzz"):
        decode(b"nope\x00")


def test_header_checked_before_anything_else():
    # Invalid utf-8 after a bad header still reports the header problem.
    with pytest.raises(ValueError) as exc:
        decode(b"xxxx\x01\xff\x00")
    assert not isinstance(exc.value, UnicodeDecodeError)


# --- Trailing data --------------------------------------------------------


def test_data_after_end_marker_is_ignored():
    assert decode(b"fuzz\x02hi\x00garbage") == ["hi"]


def test_invalid_utf8_after_end_marker_is_ignored():
    assert decode(b"fuzz\x02hi\x00\xff\xfe") == ["hi"]


def test_second_stream_after_end_marker_is_ignored():
    assert decode(encode("a") + encode("b")) == ["a"]


def test_length_token_after_end_marker_is_ignored():
    # A length that would overrun the buffer is never read.
    assert decode(b"fuzz\x00\xff") == []


# --- Input types ----------------------------------------------------------


def test_accepts_bytearray():
    assert decode(bytearray(encode("hello", "world"))) == ["hello", "world"]


def test_does_not_mutate_input():
    data = bytearray(encode("hello"))
    before = bytes(data)
    decode(data)
    assert data == before


def test_str_input_raises():
    # str has no .decode and compares unequal to b"fuzz".
    with pytest.raises(ValueError):
        decode("fuzz\x00")
