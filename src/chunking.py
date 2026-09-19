from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
    # TODO: split into sentences, group into chunks
        if not text or not text.strip():
            return []

        raw_sentences = re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = " ".join(group).strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
    # TODO: implement recursive splitting strategy
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
    # TODO: recursive helper used by RecursiveChunker.chunk
        if len(current_text) <= self.chunk_size:
            return [current_text] if current_text else []

        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ] if current_text else []

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if separator == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ] if current_text else []

        splits = current_text.split(separator)
        good_splits: list[str] = []
        for part in splits:
            if len(part) > self.chunk_size:
                sub_chunks = self._split(part, next_separators)
                good_splits.extend(sub_chunks)
            else:
                good_splits.append(part)

        merged_chunks: list[str] = []
        current_chunk = ""
        for part in good_splits:
            if not part:
                continue
            if not current_chunk:
                current_chunk = part
            else:
                candidate = current_chunk + separator + part
                if len(candidate) <= self.chunk_size:
                    current_chunk = candidate
                else:
                    merged_chunks.append(current_chunk)
                    current_chunk = part

        if current_chunk:
            merged_chunks.append(current_chunk)

        return merged_chunks if merged_chunks else [current_text]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
# TODO: implement cosine similarity formula
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    dot_val = _dot(vec_a, vec_b)
    return dot_val / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
    # TODO: call each chunker, compute stats, return comparison dict
        fixed = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        by_sentences = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def _stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_len = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            return {
                "count": count,
                "avg_length": avg_len,
                "chunks": chunks,
            }

        return {
            "fixed_size": _stats(fixed),
            "by_sentences": _stats(by_sentences),
            "recursive": _stats(recursive),
        }


class MarkdownHeadingChunker:
    """
    Split Markdown text by headings (#, ##, ###, etc.) into chunks.
    """

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        lines = text.splitlines()
        sections: list[str] = []
        current_section: list[str] = []

        for line in lines:
            if line.lstrip().startswith("#"):
                if current_section:
                    sec_str = "\n".join(current_section).strip()
                    if sec_str:
                        sections.append(sec_str)
                    current_section = []
            current_section.append(line)

        if current_section:
            sec_str = "\n".join(current_section).strip()
            if sec_str:
                sections.append(sec_str)

        final_chunks: list[str] = []
        fallback_chunker = RecursiveChunker(chunk_size=self.chunk_size)
        for sec in sections:
            if len(sec) > self.chunk_size:
                final_chunks.extend(fallback_chunker.chunk(sec))
            else:
                final_chunks.append(sec)

        return final_chunks

