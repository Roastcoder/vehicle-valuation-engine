# Vehicle Valuation API Documentation

## Base URL
```
https://your-coolify-domain.com
```

## Authentication
Set environment variables in Coolify:
- `SUREPASS_API_TOKEN` - Your Surepass RC API token
- `GEMINI_API_KEY` - Your Google Gemini API key

## Endpoints

### 1. Gemini AI Valuation (Recommended)
**Endpoint:** `POST /api/v1/idv/gemini`

**Description:** Complete vehicle valuation using just RC number. AI automatically finds prices and calculates everything.

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
    "owner_name": "John Doe",
    "raw_data": {
      "maker_model": "SWIFT VXI",
      "manufacturing_date_formatted": "2019-12",
      "fuel_type": "PETROL",
      "owner_number": "1"
    }
  },
  "idv_calculation": {
    "vehicle_make": "Maruti Suzuki",
    "vehicle_model": "SWIFT VXI",
    "manufacturing_year": "2019",
    "vehicle_age": "5 years 1 months",
    "owner_count": 1,
    "current_ex_showroom": 650000,
    "estimated_odometer": 60000,
    "base_depreciation_percent": 40,
    "book_value": 390000,
    "market_listings_mean": 425000,
    "fair_market_retail_value": 389250,
    "dealer_purchase_price": 342425,
    "confidence_score": 85,
    "ai_model": "gemini-3-pro-preview"
  }
}
```

**cURL Example:**
```bash
curl -X POST https://your-domain.com/api/v1/idv/gemini \
  -H "Content-Type: application/json" \
  -d '{"rc_number": "DL08AB1234"}'
```

**Python Example:**
```python
import requests

response = requests.post(
    'https://your-domain.com/api/v1/idv/gemini',
    json={'rc_number': 'DL08AB1234'}
)

data = response.json()
if data['success']:
    valuation = data['idv_calculation']
    print(f"Fair Market Value: ₹{valuation['fair_market_retail_value']:,}")
    print(f"Dealer Price: ₹{valuation['dealer_purchase_price']:,}")
    print(f"AI Confidence: {valuation['confidence_score']}%")
```

**JavaScript Example:**
```javascript
fetch('https://your-domain.com/api/v1/idv/gemini', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ rc_number: 'DL08AB1234' })
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    console.log('Fair Market Value:', data.idv_calculation.fair_market_retail_value);
    console.log('Dealer Price:', data.idv_calculation.dealer_purchase_price);
  }
});
```

---

### 2. Manual Valuation
**Endpoint:** `POST /api/v1/valuation/manual`

**Request:**
```json
{
  "make": "Maruti Suzuki",
  "model": "Swift",
  "fuel_type": "Petrol",
  "reg_date": "2019-03-15",
  "rto_code": "DL3C",
  "city": "Delhi",
  "body_type": "Hatchback",
  "color": "White",
  "current_ex_showroom": 650000,
  "market_listings_mean": 425000
}
```

---

### 3. RC API Valuation
**Endpoint:** `POST /api/v1/valuation/rc`

**Request:**
```json
{
  "rc_number": "DL08AB1234",
  "current_ex_showroom": 650000,
  "market_listings_mean": 425000
}
```

---

### 4. Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Vehicle Valuation Engine",
  "version": "1.0.0"
}
```

---

## Features

### 6-Layer Valuation Architecture
1. **Derived Metrics** - Age, odometer, mileage analysis
2. **Base Depreciation** - Standard grid (5%-60%)
3. **Market Intelligence** - Discontinued models, new gen, color, owner count
4. **Regional Logic** - NCR diesel ban, South India premium, coastal corrosion
5. **Valuation Convergence** - Market listing integration
6. **Dealer Economics** - Margins and refurbishment costs

### AI Capabilities
- **Gemini 3.0 Pro** - Latest AI model
- **Dual-Engine** - ICE and EV valuation
- **Machine Learning** - Pattern recognition, anomaly detection
- **Neural Networks** - Multi-factor correlation
- **Deep Learning** - NLP, sentiment analysis
- **Predictive Analytics** - Future value forecasting

### EV Support
- Battery SoH calculation
- Chemistry-based degradation (NMC/LFP)
- Warranty cliff analysis
- Replacement cost estimation

### Owner Count Penalty
- 1st owner: No penalty
- 2nd owner: -4% value
- 3rd owner: -8% value
- 4th+ owner: -12% value

---

## Error Responses

**400 Bad Request:**
```json
{
  "success": false,
  "error": "Missing required field: rc_number"
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "error": "API token not configured"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Gemini API error: ..."
}
```

---

## Rate Limits
- No rate limits currently
- Recommended: Max 100 requests/minute per user

## Support
- GitHub: [Your Repository URL]
- Email: [Your Email]
