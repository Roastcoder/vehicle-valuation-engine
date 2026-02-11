# Gemini-Powered IDV Calculation Engine

## Overview

Automated IDV (Insured Declared Value) calculation system that uses Google Gemini AI to automatically find historical on-road prices and calculate insurance values.

## Complete Workflow

```
User Enters RC Number
        ↓
Call RC API (Surepass)
        ↓
Normalize Vehicle Data
        ↓
Send Structured Prompt to Gemini
        ↓
Gemini Finds Historical On-Road Price
        ↓
Gemini Calculates IDV
        ↓
Backend Validates 20% Rule
        ↓
Final IDV Response
```

## Key Features

✅ **Automatic Price Discovery**
- Gemini searches for year-specific on-road prices
- No manual price input required
- Handles ex-showroom to on-road conversion

✅ **Manufacturing Date-Based Depreciation**
- Uses `manufacturing_date_formatted` (NOT registration_date)
- Separate depreciation schedules for 2W and 4W
- Age calculated in years and months

✅ **Market Validation**
- Gemini finds current market median prices
- Backend validates with 20% threshold
- Automatic confidence scoring

✅ **Variant Matching**
- Exact model + CC + BS norms matching
- Avoids facelift/new generation confusion
- High accuracy variant identification

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
export SUREPASS_API_TOKEN="your_surepass_token"
export GEMINI_API_KEY="your_gemini_api_key"
```

### 3. Get Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and set as environment variable

## Usage

### Method 1: Python Module

```python
from gemini_idv_engine import calculate_idv_with_gemini

result = calculate_idv_with_gemini(
    rc_number="DL08AB1234",
    surepass_token="your_token",
    gemini_api_key="your_key"
)

if result['success']:
    idv = result['idv_calculation']
    print(f"Calculated IDV: ₹{idv['calculated_idv']:,.2f}")
    print(f"Validation: {idv['validation_status']}")
```

### Method 2: REST API

```bash
curl -X POST http://localhost:5000/api/v1/idv/gemini \
  -H "Content-Type: application/json" \
  -d '{
    "rc_number": "DL08AB1234"
  }'
```

## API Endpoint

### POST /api/v1/idv/gemini

**Request:**
```json
{
  "rc_number": "DL08AB1234"
}
```

**Response:**
```json
{
  "success": true,
  "rc_details": {
    "rc_number": "DL08AB1234",
    "make": "Honda",
    "model": "ACTIVA 5G",
    "manufacturing_date": "2017-12"
  },
  "idv_calculation": {
    "vehicle_type": "2W",
    "vehicle_make": "Honda",
    "vehicle_model": "ACTIVA 5G",
    "variant": "ACTIVA 5G 109.19cc BS4",
    "manufacturing_year": "2017",
    "city_used_for_price": "Delhi",
    "original_on_road_price": 66000,
    "vehicle_age": "7 years 1 months",
    "depreciation_percent": 65,
    "calculated_idv": 23100,
    "market_median_estimate": 42000,
    "difference_percent": 45.0,
    "validation_status": "Manual Review Required",
    "confidence_score": 65
  }
}
```

## Depreciation Schedules

### 2-Wheeler (Scooter/Motorcycle)
| Age | Depreciation |
|-----|--------------|
| < 6 months | 5% |
| 6 months - 1 year | 15% |
| 1 - 2 years | 20% |
| 2 - 3 years | 30% |
| 3 - 4 years | 40% |
| 4 - 5 years | 50% |
| 5 - 7 years | 60% |
| > 7 years | 65% |

### 4-Wheeler (Car/LMV)
| Age | Depreciation |
|-----|--------------|
| < 6 months | 5% |
| 6 months - 1 year | 15% |
| 1 - 2 years | 20% |
| 2 - 3 years | 30% |
| 3 - 4 years | 40% |
| 4 - 5 years | 50% |
| 5 - 7 years | 55% |
| 7 - 10 years | 65% |
| > 10 years | 70% |

## Validation Rules

### 20% Threshold Rule

```python
difference = |calculated_idv - market_median| / market_median × 100

if difference > 20%:
    validation_status = "Manual Review Required"
else:
    validation_status = "Within Acceptable Range"
```

### Confidence Scoring

- Base confidence: 85%
- If market validation fails: -20%
- If no market data: 75%
- Final score: max(0, base + adjustments)

## Gemini Prompt Structure

The system sends a structured prompt to Gemini with:

1. **Vehicle Details**
   - Type (2W/4W)
   - Make, Model, Variant
   - Engine capacity, BS norms
   - Manufacturing date
   - City

2. **Task Instructions**
   - Find year-specific on-road price
   - Calculate age from manufacturing date
   - Apply correct depreciation schedule
   - Find market median
   - Return JSON only

3. **Output Format**
   - Strict JSON schema
   - No explanations
   - All required fields

## Testing

```bash
# Test Gemini IDV engine
python3 test_gemini_idv.py

# Test with real API (requires keys)
export GEMINI_API_KEY="your_key"
python3 test_gemini_idv.py
```

## Error Handling

### Common Errors

1. **GEMINI_API_KEY not configured**
   ```
   Solution: Set environment variable
   export GEMINI_API_KEY="your_key"
   ```

2. **Failed to parse Gemini response**
   ```
   Solution: Check Gemini API quota/limits
   Verify prompt structure
   ```

3. **RC API failed**
   ```
   Solution: Verify SUREPASS_API_TOKEN
   Check RC number format
   ```

## Advantages Over Manual IDV

| Feature | Manual IDV | Gemini IDV |
|---------|-----------|------------|
| Price Input | Manual entry required | Automatic discovery |
| Variant Matching | Manual research | AI-powered matching |
| Market Validation | Optional | Automatic |
| Speed | Slow | Fast (< 5 seconds) |
| Accuracy | Depends on user | AI + Backend validation |
| Scalability | Limited | High |

## Production Deployment

### Environment Variables
```bash
export SUREPASS_API_TOKEN="your_surepass_token"
export GEMINI_API_KEY="your_gemini_key"
export FLASK_ENV="production"
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV SUREPASS_API_TOKEN=""
ENV GEMINI_API_KEY=""
CMD ["python3", "api_server.py"]
```

### Rate Limiting
- Gemini API: 60 requests/minute (free tier)
- Surepass API: Check your plan limits
- Implement caching for repeated RC lookups

## Cost Estimation

### Per IDV Calculation
- Surepass RC API: ~₹2-5 per call
- Gemini API: Free tier (60 RPM)
- Total: ~₹2-5 per calculation

### Monthly (1000 calculations)
- Surepass: ₹2,000 - ₹5,000
- Gemini: Free (within limits)
- Total: ₹2,000 - ₹5,000

## Support

For issues:
1. Check API keys are configured
2. Verify RC number format
3. Review Gemini API quota
4. Check test files for examples

## License

Proprietary - Automotive FinTech Solution
