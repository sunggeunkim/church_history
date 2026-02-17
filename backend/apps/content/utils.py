"""Utility functions for content processing and text chunking."""

import re
from typing import List, Tuple


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: The text to count tokens for

    Returns:
        Number of tokens in the text
    """
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-3.5/GPT-4 encoding
        return len(encoding.encode(text))
    except ImportError:
        # Fallback: rough approximation (1 token ~= 4 characters)
        return len(text) // 4


def clean_transcript(text: str) -> str:
    """
    Clean YouTube transcript text.

    Removes timestamps, excessive whitespace, and fixes common transcript issues.

    Args:
        text: Raw transcript text

    Returns:
        Cleaned transcript text
    """
    # Remove timestamps in various formats: [00:05:30], (00:05:30), 00:05:30
    text = re.sub(r'\[?\(?\d{1,2}:\d{2}:\d{2}\)?\]?', '', text)
    text = re.sub(r'\[?\(?\d{1,2}:\d{2}\)?\]?', '', text)

    # Remove music/sound effect annotations
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?music.*?\)', '', text, flags=re.IGNORECASE)

    # Fix multiple spaces
    text = re.sub(r' +', ' ', text)

    # Fix multiple newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)

    # Fix encoding issues (common transcription artifacts)
    replacements = {
        '\u2018': "'", '\u2019': "'",  # Smart single quotes
        '\u201c': '"', '\u201d': '"',  # Smart double quotes
        '\u2013': '-', '\u2014': '--',  # En/em dashes
        '\u2026': '...',  # Ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50) -> List[Tuple[str, int]]:
    """
    Split text into overlapping chunks with token limits.

    Attempts to split on paragraph/sentence boundaries for cleaner chunks.

    Args:
        text: The text to chunk
        max_tokens: Target maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks

    Returns:
        List of tuples (chunk_text, token_count)
    """
    if not text or not text.strip():
        return []

    # First split by paragraphs (double newlines)
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = []
    current_tokens = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        para_tokens = count_tokens(paragraph)

        # If single paragraph exceeds max_tokens, split by sentences
        if para_tokens > max_tokens:
            sentences = _split_sentences(paragraph)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                sent_tokens = count_tokens(sentence)

                # If single sentence is too long, split by words
                if sent_tokens > max_tokens:
                    word_chunks = _split_by_words(sentence, max_tokens)
                    for word_chunk in word_chunks:
                        chunks.append((word_chunk, count_tokens(word_chunk)))
                    continue

                # Check if adding sentence exceeds limit
                if current_tokens + sent_tokens > max_tokens and current_chunk:
                    # Save current chunk
                    chunk_text = ' '.join(current_chunk)
                    chunks.append((chunk_text, count_tokens(chunk_text)))

                    # Start new chunk with overlap
                    if overlap > 0:
                        current_chunk = _get_overlap_text(current_chunk, overlap)
                        current_tokens = count_tokens(' '.join(current_chunk))
                    else:
                        current_chunk = []
                        current_tokens = 0

                current_chunk.append(sentence)
                current_tokens += sent_tokens
        else:
            # Paragraph fits within limit, check if adding to current chunk
            if current_tokens + para_tokens > max_tokens and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append((chunk_text, count_tokens(chunk_text)))

                # Start new chunk with overlap
                if overlap > 0:
                    current_chunk = _get_overlap_text(current_chunk, overlap)
                    current_tokens = count_tokens('\n\n'.join(current_chunk))
                else:
                    current_chunk = []
                    current_tokens = 0

            current_chunk.append(paragraph)
            current_tokens += para_tokens

    # Add remaining chunk
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk) if isinstance(current_chunk[0], str) and '\n' in text else ' '.join(current_chunk)
        chunks.append((chunk_text, count_tokens(chunk_text)))

    return chunks


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitter (can be improved with nltk if needed)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]


def _split_by_words(text: str, max_tokens: int) -> List[str]:
    """Split text by words when sentences are too long."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = count_tokens(word)
        if current_tokens + word_tokens > max_tokens and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def _get_overlap_text(chunks: List[str], overlap_tokens: int) -> List[str]:
    """Get the last N tokens worth of text for overlap."""
    if not chunks:
        return []

    # Start from the end and work backwards until we have enough tokens
    overlap_chunks = []
    total_tokens = 0

    for chunk in reversed(chunks):
        chunk_tokens = count_tokens(chunk)
        if total_tokens + chunk_tokens <= overlap_tokens:
            overlap_chunks.insert(0, chunk)
            total_tokens += chunk_tokens
        else:
            # Split the chunk to get exactly the overlap we need
            words = chunk.split()
            for word in reversed(words):
                word_tokens = count_tokens(word)
                if total_tokens + word_tokens <= overlap_tokens:
                    overlap_chunks.insert(0, word)
                    total_tokens += word_tokens
                else:
                    break
            break

    return overlap_chunks
