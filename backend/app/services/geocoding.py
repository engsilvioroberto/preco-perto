"""
Geocoding service using Nominatim (OpenStreetMap).
Converts addresses to latitude/longitude coordinates.
"""

import hashlib
import json
import logging
from typing import Optional

import redis
import requests

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "PrecoPerto/1.0"}
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

# Redis connection (lazy singleton)
_redis_client: Optional[redis.Redis] = None


def _get_redis() -> Optional[redis.Redis]:
    """Return a Redis client, or None if connection fails."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        from app.core.config import settings as app_settings
        _redis_client = redis.Redis.from_url(
            app_settings.REDIS_URL, decode_responses=True
        )
        _redis_client.ping()
        return _redis_client
    except Exception as exc:
        logger.warning("Redis unavailable, geocoding cache disabled: %s", exc)
        _redis_client = None
        return None


def _cache_key(address: str) -> str:
    """Generate a deterministic cache key for an address."""
    normalized = address.strip().lower()
    digest = hashlib.md5(normalized.encode()).hexdigest()
    return f"geocode:{digest}"


def geocode_address(address: str) -> Optional[dict]:
    """
    Geocode an address string to latitude/longitude using Nominatim.

    Args:
        address: Full address string (e.g. 'Av. Presidente Vargas, 2001, Ribeirão Preto')

    Returns:
        dict with keys 'lat', 'lng', 'display_name' or None on failure.
    """
    if not address or not address.strip():
        return None

    # Check cache first
    r = _get_redis()
    key = _cache_key(address)
    if r:
        try:
            cached = r.get(key)
            if cached:
                logger.debug("Cache hit for address: %s", address)
                return json.loads(cached)
        except Exception as exc:
            logger.warning("Redis read error: %s", exc)

    # Call Nominatim
    try:
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
        }
        response = requests.get(
            NOMINATIM_URL, params=params, headers=HEADERS, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.info("No geocoding result for: %s", address)
            return None

        result = {
            "lat": float(data[0]["lat"]),
            "lng": float(data[0]["lon"]),
            "display_name": data[0].get("display_name", address),
        }

        # Store in cache
        if r:
            try:
                r.setex(key, CACHE_TTL_SECONDS, json.dumps(result))
            except Exception as exc:
                logger.warning("Redis write error: %s", exc)

        return result

    except requests.RequestException as exc:
        logger.error("Nominatim request failed for '%s': %s", address, exc)
        return None
    except (ValueError, KeyError, IndexError) as exc:
        logger.error("Failed to parse Nominatim response: %s", exc)
        return None
