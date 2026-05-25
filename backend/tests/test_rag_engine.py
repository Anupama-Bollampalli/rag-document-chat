import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag_engine import _chunk_text


def test_chunk_text_basic():
    text = "A" * 1200
    chunks = _chunk_text(text)
    assert len(chunks) >= 2, "1200 chars should produce multiple chunks"
    for c in chunks:
        assert len(c) <= 500 + 50, "Each chunk should not exceed CHUNK_SIZE + overlap"


def test_chunk_text_small_input():
    text = "Short text."
    chunks = _chunk_text(text)
    assert chunks == [], "Chunks shorter than min length should be filtered"


def test_chunk_text_overlap():
    text = "word " * 150  # 750 chars
    chunks = _chunk_text(text)
    assert len(chunks) >= 2
    # Last char of chunk 1 should appear near start of chunk 2 (overlap)
    if len(chunks) >= 2:
        end_of_chunk1 = chunks[0][-50:]
        start_of_chunk2 = chunks[1][:100]
        assert any(word in start_of_chunk2 for word in end_of_chunk1.split()[-3:]), \
            "Chunks should overlap"


def test_chunk_preserves_content():
    text = "The quick brown fox jumps over the lazy dog. " * 20
    chunks = _chunk_text(text)
    rejoined = " ".join(chunks)
    for word in ["quick", "brown", "fox", "lazy", "dog"]:
        assert word in rejoined, f"'{word}' should appear in chunks"
