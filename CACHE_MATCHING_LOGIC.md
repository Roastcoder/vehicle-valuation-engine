# Cache Matching Logic for Same Vehicle Details

## Matching Criteria

The system returns **EXACT SAME VALUES** for vehicles matching these criteria:

### 1. Primary Matching Fields
```python
{
    "vehicle_make": "SKODA AUTO VOLKSWAGEN",      # Cleaned (no INDIA LTD, etc.)
    "vehicle_model": "VIRTUS",                     # Base model only (first word)
    "manufacturing_year": "2024",                  # Year only (YYYY)
    "city": "MUMBAI"                               # City from registered_at
}
```

### 2. What Gets Matched
✅ **Same Make + Model + Year + City** → Returns cached values
- Example 1: `VIRTUS 2024 Mumbai` 
- Example 2: `VIRTUS GT LINE 1.0 TSI AT 2024 Mumbai`
- **Result:** Both get SAME cached values (base model "VIRTUS" matches)

### 3. What Does NOT Match
❌ Different values trigger new calculation:
- Different manufacturing year: `2024` vs `2023`
- Different city: `Mumbai` vs `Delhi`
- Different model: `VIRTUS` vs `VENTO`
- Different make: `Volkswagen` vs `Honda`

## Cache Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: RC API Call                                         │
│ Input: RC Number (e.g., mh47bz1005)                        │
│ Output: Vehicle details                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Extract Matching Keys                              │
│ - vehicle_make: "SKODA AUTO VOLKSWAGEN"                    │
│ - vehicle_model: "VIRTUS" (base model)                     │
│ - manufacturing_year: "2024"                                │
│ - city: "MUMBAI"                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Database Lookup                                     │
│ Query: SELECT * FROM valuations                            │
│        WHERE vehicle_make = 'SKODA AUTO VOLKSWAGEN'        │
│          AND vehicle_model = 'VIRTUS'                       │
│          AND manufacturing_year = '2024'                    │
│          AND created_at >= NOW() - 90 days                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    │               │
              ✅ FOUND          ❌ NOT FOUND
                    │               │
                    ↓               ↓
        ┌───────────────────┐  ┌──────────────────────┐
        │ Return Cached     │  │ Call SearchAPI +     │
        │ Values (Instant)  │  │ Gemini (~8s)         │
        │                   │  │                      │
        │ - Update age      │  │ - Get market prices  │
        │ - Update odometer │  │ - Calculate IDV      │
        │ - Return same     │  │ - Save to database   │
        │   prices          │  │ - Return new values  │
        └───────────────────┘  └──────────────────────┘
```

## Example Scenarios

### Scenario 1: Exact Match (Cache Hit)
```json
// First Request: mh47bz1005
{
  "vehicle_make": "SKODA AUTO VOLKSWAGEN",
  "vehicle_model": "VIRTUS",
  "manufacturing_year": "2024",
  "city": "MUMBAI",
  "fair_market_retail_value": 1370625
}

// Second Request: mh02gj2882 (Same specs)
{
  "vehicle_make": "SKODA AUTO VOLKSWAGEN",
  "vehicle_model": "VIRTUS",
  "manufacturing_year": "2024",
  "city": "MUMBAI",
  "fair_market_retail_value": 1370625  // ✅ SAME VALUE
}
```

### Scenario 2: Different Month (Still Matches)
```json
// Vehicle 1: 2024-11 (November)
// Vehicle 2: 2024-12 (December)
// Result: ✅ MATCH (only year matters, not month)
// Only age and odometer are recalculated
```

### Scenario 3: Different City (No Match)
```json
// Vehicle 1: Mumbai
// Vehicle 2: Delhi
// Result: ❌ NO MATCH (different cities)
// New calculation triggered
```

## Database Schema

```sql
CREATE TABLE valuations (
    id INTEGER PRIMARY KEY,
    vehicle_make TEXT,           -- Matching field 1
    vehicle_model TEXT,          -- Matching field 2
    manufacturing_year TEXT,     -- Matching field 3
    city TEXT,                   -- Matching field 4
    fair_market_retail_value REAL,
    dealer_purchase_price REAL,
    current_ex_showroom REAL,
    market_listings_mean REAL,
    confidence_score REAL,
    created_at TIMESTAMP,
    -- Other fields...
);

-- Index for fast lookup
CREATE INDEX idx_vehicle_match 
ON valuations(vehicle_make, vehicle_model, manufacturing_year, city);
```

## Cache Validity

- **Duration:** 90 days
- **Reason:** Market prices change over time
- **After 90 days:** New calculation triggered even for same vehicle

## Dynamic Fields (Updated on Cache Hit)

These fields are recalculated even when using cache:

1. **vehicle_age** - Based on current date
2. **estimated_odometer** - Based on months since manufacturing

Example:
```json
// Cached on: 2026-01-01
{
  "vehicle_age": "1 years 1 months",
  "estimated_odometer": 13000
}

// Retrieved on: 2026-02-01 (1 month later)
{
  "vehicle_age": "1 years 2 months",  // ✅ Updated
  "estimated_odometer": 14000          // ✅ Updated
}
```

## Performance Metrics

| Scenario | Time | API Calls |
|----------|------|-----------|
| **Cache Hit** | <1s | 0 (Database only) |
| **Cache Miss** | ~8s | 2 (SearchAPI + Gemini) |
| **Savings** | 87.5% | 100% |

## Code Reference

**Cache Check:** `gemini_idv_engine.py` Line 47-73
```python
cached = db.get_exact_match_valuation(
    vehicle_make, 
    vehicle_model, 
    manufacturing_year, 
    city
)

if cached:
    print(f"✅ CACHE HIT: Found {vehicle_make} {vehicle_model} {manufacturing_year}")
    # Update dynamic fields
    # Return cached values
```

**Database Method:** `database.py` Line 383+
```python
def get_exact_match_valuation(self, vehicle_make, vehicle_model, 
                               manufacturing_year, city):
    """Get exact match valuation without variant dependency"""
    # Query database with 4 matching criteria
    # Return cached result if found within 90 days
```
