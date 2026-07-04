# PreçoPerto Backend Services - Implementation Summary

## Services Implemented

### 1. Geocoding Service (`app/services/geocoding.py`)
- **Function**: `geocode_address(address: str) -> Optional[dict]`
- **Features**:
  - Uses Nominatim (OpenStreetMap) API
  - Required User-Agent header: "PrecoPerto/1.0"
  - Redis cache with 7-day TTL (graceful degradation if Redis unavailable)
  - Returns dict with `lat`, `lng`, `display_name` or None on failure
- **Test Results**:
  - ✅ Cache key generation works
  - ✅ Empty input handling returns None
  - ✅ Real geocoding works: "Av. Presidente Vargas, 2001, Ribeirão Preto" → lat=-21.205473, lng=-47.8101313
  - ✅ Graceful degradation when Redis unavailable

### 2. Product Normalization Service (`app/services/product_normalization.py`)
- **Functions**:
  - `normalize_product(name: str) -> str`: Standardizes product names
  - `fuzzy_match(name1: str, name2: str) -> float`: Returns similarity score 0-100%
- **Features**:
  - Lowercase conversion
  - Accent removal (unicodedata.normalize)
  - Special character removal
  - Unit standardization:
    - Volume: "1 litro" = "1000ml" = "1l", "2 litros" = "2l"
    - Weight: "1 quilo" = "1000g" = "1kg", "5 quilos" = "5kg"
  - Uses rapidfuzz for fuzzy matching (token_sort_ratio)
- **Test Results**:
  - ✅ normalize_product('Leite Integral 1L') → 'leite integral 1l'
  - ✅ Accent removal: 'Café Torrado 1kg' → 'cafe torrado 1kg'
  - ✅ Unit normalization: 'Leite 1000ml' → 'leite 1.0l'
  - ✅ fuzzy_match('Leite Integral 1L', 'Leite integral 1 litro') → 100%
  - ✅ fuzzy_match('Coca-Cola 2L', 'Pepsi 2L') → 30% (different products)
  - ✅ fuzzy_match('Arroz Branco 5kg', 'arroz branco 5 quilos') → 100%

### 3. Distance Calculation Service (`app/services/utils/distance.py`)
- **Functions**:
  - `calculate_distance(lat1, lng1, lat2, lng2) -> float`: Returns distance in km
  - `calculate_cost_benefit(distance_km, price_diff) -> dict`: Cost-benefit analysis
- **Features**:
  - Haversine formula for great-circle distance
  - Transport cost calculations (round trip):
    - Walking: 5 km/h, R$0/km
    - Car: 30 km/h, R$0.75/km (gas + maintenance)
    - Bus: R$4.40 fixed fare (Ribeirão Preto)
  - Returns transport costs, time estimates, and worth_it flags
- **Test Results**:
  - ✅ calculate_distance(-21.1767, -47.8208, -21.1900, -47.8100) → 1.85 km
  - ✅ cost_benefit(1.5km, R$3.00):
    - Walking: R$0.00 (worth it: True)
    - Car: R$2.25 (worth it: True)
    - Bus: R$8.80 (worth it: False)
  - ✅ cost_benefit(0.5km, R$10.00): All modes worth it

## Dependencies Installed
- `redis` (8.0.1) - Redis client for caching
- `rapidfuzz` (3.14.5) - Fuzzy string matching
- `requests` (2.34.2) - HTTP client for Nominatim API

## Files Created
```
/opt/data/preco-perto/backend/
├── app/
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── geocoding.py
│       ├── product_normalization.py
│       └── utils/
│           ├── __init__.py
│           └── distance.py
├── test_geocoding.py (temporary test file)
└── venv/ (Python virtual environment)
```

## Notes
- All services are independently testable
- Geocoding service gracefully handles Redis unavailability
- Product normalization handles Brazilian Portuguese units correctly
- Distance calculations use real-world transport costs for Ribeirão Preto
- All services include proper error handling and logging
