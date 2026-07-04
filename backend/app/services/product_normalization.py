"""
Product normalization and fuzzy matching service.
Standardizes product names and compares similarity.
"""

import re
import unicodedata

from rapidfuzz import fuzz


# Unit normalization mappings (applied after lowercasing and accent removal)
# Use capture groups to preserve the number
UNIT_REPLACEMENTS = [
    # Volume: convert to liters
    (r'\b(\d+)\s*litros?\b', r'\1l'),
    (r'\b(\d+)\s*ml\b', lambda m: f'{int(m.group(1))/1000}l' if int(m.group(1)) >= 1000 else f'{m.group(1)}ml'),
    # Weight: convert to kg
    (r'\b(\d+)\s*quilos?\b', r'\1kg'),
    (r'\b(\d+)\s*g\b', lambda m: f'{int(m.group(1))/1000}kg' if int(m.group(1)) >= 1000 else f'{m.group(1)}g'),
]


def _remove_accents(text: str) -> str:
    """Remove diacritics/accents from text."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _remove_special_chars(text: str) -> str:
    """Remove special characters, keeping only alphanumeric, spaces, and basic symbols."""
    # Keep letters, digits, spaces, %, /, and common unit chars
    text = re.sub(r"[^\w\s%\/]", " ", text, flags=re.UNICODE)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_product(name: str) -> str:
    """
    Normalize a product name for consistent comparison.

    Steps:
    1. Lowercase
    2. Remove accents
    3. Remove special characters
    4. Standardize units (1L, 1kg, etc.)

    Args:
        name: Raw product name (e.g. 'Leite Integral 1L')

    Returns:
        Normalized string (e.g. 'leite integral 1l')
    """
    if not name:
        return ""

    # Step 1: lowercase
    text = name.lower()

    # Step 2: remove accents
    text = _remove_accents(text)

    # Step 3: remove special characters
    text = _remove_special_chars(text)

    # Step 4: standardize units
    for pattern, replacement in UNIT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)

    # Final cleanup: collapse spaces again
    text = re.sub(r"\s+", " ", text).strip()

    return text


def fuzzy_match(name1: str, name2: str) -> float:
    """
    Calculate fuzzy similarity between two product names.

    Uses token_sort_ratio from rapidfuzz for order-independent comparison
    after normalizing both names.

    Args:
        name1: First product name
        name2: Second product name

    Returns:
        Similarity score from 0.0 to 100.0 (percentage).
    """
    norm1 = normalize_product(name1)
    norm2 = normalize_product(name2)

    if not norm1 or not norm2:
        return 0.0

    # token_sort_ratio handles word order differences
    score = fuzz.token_sort_ratio(norm1, norm2)
    return float(score)
