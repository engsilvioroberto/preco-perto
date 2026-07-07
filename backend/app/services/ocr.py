"""
OCR service for offer flyer processing.
Uses pytesseract (server-side) to extract text from uploaded images,
then parses product/price pairs from promotional flyers.
"""

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


def extract_text_from_image(image_path: str, lang: str = "por") -> str:
    """
    Extract text from an image using pytesseract.
    Runs in a thread pool (call via asyncio.to_thread) to avoid blocking.
    """
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except ImportError:
        logger.error(
            "pytesseract or Pillow not installed. "
            "Install with: pip install pytesseract Pillow"
        )
        raise
    except Exception as exc:
        logger.error("OCR extraction failed: %s", exc)
        raise


def parse_offer_flyer(text: str) -> List[dict]:
    """
    Parse offer flyer OCR text to extract product/price pairs.

    Heuristic approach:
    1. Find all R$ prices in the text
    2. For each price, extract nearby text as the product description
    3. Score confidence based on regex match quality

    Returns list of dicts: {description, price, original_price, confidence}
    """
    items = []
    lines = text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # Pattern: "R$ XX,XX" or "R$XX,XX" or "XX,XX" near product text
    price_pattern = re.compile(r"R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})")

    for i, line in enumerate(lines):
        matches = price_pattern.findall(line)
        if not matches:
            continue

        # The product name is on the same line before the price,
        # or on the previous line
        product_name = ""
        for price_str in matches:
            price_val = _parse_brl(price_str)
            if price_val is None or price_val <= 0:
                continue

            # Try to extract product name from the same line
            line_before_price = line
            for p in re.finditer(price_pattern, line):
                name_part = line[: p.start()].strip()
                if name_part:
                    product_name = name_part.rstrip(":,;-")
                else:
                    # Check previous line
                    if i > 0:
                        prev = lines[i - 1]
                        # Skip if previous line also has a price (it's a different item)
                        if not price_pattern.search(prev):
                            product_name = prev.rstrip(":,;-")

            if not product_name:
                continue

            # Look for "de R$" or "De:" pattern for original_price
            original_price = None
            de_match = re.search(
                r"(?:de|DE|De|por|POR|Por)\s*:?\s*R?\$?\s*("
                r"\d{1,3}(?:\.\d{3})*,\d{2})",
                line,
            )
            if de_match:
                original_price = _parse_brl(de_match.group(1))

            description = product_name.strip()
            if not description or len(description) < 3:
                continue

            # Confidence: lower if product name is very short or contains
            # only numbers/price-like fragments
            confidence = _compute_confidence(description, price_val)

            items.append({
                "description": description,
                "price": price_val,
                "original_price": original_price,
                "confidence": confidence,
            })

    # Deduplicate by description + price
    seen = set()
    unique_items = []
    for item in items:
        key = (item["description"].lower(), item["price"])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items


def _parse_brl(value: str) -> Optional[float]:
    """Parse Brazilian currency string '1.234,56' -> 1234.56"""
    try:
        cleaned = value.replace(".", "").replace(",", ".")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def _compute_confidence(description: str, price: float) -> float:
    """Heuristic confidence score 0-100."""
    score = 85.0  # base

    if len(description) < 5:
        score -= 20
    if len(description) > 50:
        score -= 10
    if not re.search(r"[a-zA-Z]", description):
        score -= 30
    if price <= 0:
        score -= 50

    return max(10.0, min(99.0, score))
