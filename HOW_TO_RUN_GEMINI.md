# How to Run Gemini-Powered IDV Calculation

## Step 1: Set API Keys

```bash
export GEMINI_API_KEY="AIzaSyC18vQLa1_HorosTsQvL3YY0B2VbQeOhxc"
export SUREPASS_API_TOKEN="your_surepass_token_here"
```

## Step 2: Start the Server

```bash
cd "/Users/yogii/Desktop/resale calculaator"
python3 api_server.py
```

Server will start on: **http://localhost:5000**

## Step 3: Test Gemini IDV

### Option A: Using Python Script
```bash
python3 run_gemini_test.py
```

### Option B: Using curl
```bash
curl -X POST http://localhost:5000/api/v1/idv/gemini \
  -H "Content-Type: application/json" \
  -d '{
    "rc_number": "DL08AB1234"
  }'
```

### Option C: Using Postman/Insomnia

**Endpoint:** `POST http://localhost:5000/api/v1/idv/gemini`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "rc_number": "DL08AB1234"
}
```

## What Happens?

1. **RC API Call** → Fetches vehicle details from RTO
2. **Gemini AI** → Finds historical on-road price for manufacturing year
3. **Age Calculation** → Uses manufacturing_date_formatted (NOT registration_date)
4. **Depreciation** → Applies 2W/4W specific depreciation schedule
5. **IDV Calculation** → Computes final IDV
6. **Validation** → Checks against market median (20% threshold)

## Expected Response

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

## Troubleshooting

### Error: "Gemini API key not configured"
```bash
export GEMINI_API_KEY="your_key_here"
```

### Error: "Surepass API token not configured"
```bash
export SUREPASS_API_TOKEN="your_token_here"
```

### Error: "Connection refused"
Make sure server is running:
```bash
python3 api_server.py
```

## Key Features

✅ **Zero Manual Input** - Just provide RC number
✅ **Automatic Price Discovery** - Gemini finds historical prices
✅ **Manufacturing Date-Based** - Correct age calculation
✅ **Market Validation** - 20% threshold check
✅ **Confidence Scoring** - Reliability indicator
