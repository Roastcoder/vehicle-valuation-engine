# Used Vehicle Resale Value Predictor - Indian Market

A robust Python-based valuation engine for calculating fair market retail value and dealer purchase prices for used vehicles in India. Now includes **Gemini AI-powered IDV calculation** for motor insurance.

## Features

### 6-Layer Valuation Architecture

1. **Derived Metrics**: Age calculation, odometer estimation, mileage deviation analysis
2. **Base Depreciation**: Standard depreciation grid with reverse inflation modeling
3. **Market Intelligence**: Discontinued models, new generation launches, color factors
4. **Regional Logic**: NCR diesel ban, South India premium, coastal corrosion
5. **Valuation Convergence**: Market listing integration with negotiation gap
6. **Dealer Economics**: Body-type specific margins and refurbishment costs

### RC API Integration

- **Surepass RC API**: Automatic vehicle data fetching from RTO records
- **Auto-parsing**: Converts RC data to valuation format
- **Complete workflow**: Single function call for RC fetch + valuation

### 🆕 Gemini AI-Powered IDV Calculation

- **Automatic Price Discovery**: Gemini finds historical on-road prices
- **Manufacturing Date-Based**: Uses `manufacturing_date_formatted` (NOT registration_date)
- **Market Validation**: 20% threshold with confidence scoring
- **Zero Manual Input**: Just provide RC number, get complete IDV

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

```bash
export SUREPASS_API_TOKEN="your_surepass_token"
export GEMINI_API_KEY="your_gemini_key"  # Get from https://makersuite.google.com/app/apikey
```

## Usage

### Method 1: Manual Vehicle Data Input

```python
from vehicle_valuation import calculate_resale_value

vehicle_data = {
    'make': 'Maruti Suzuki',
    'model': 'Swift',
    'variant': 'VXI',
    'fuel_type': 'Petrol',
    'reg_date': '2019-03-15',
    'rto_code': 'DL3C',
    'city': 'Delhi',
    'body_type': 'Hatchback',
    'color': 'White',
    'owner_count': 1,
    'current_ex_showroom': 650000,
    'market_listings_mean': 425000,
    'odometer': 45000
}

result = calculate_resale_value(vehicle_data)
print(result)
```

### Method 2: RC API Integration (Auto-Fetch)

```python
from rc_api_integration import get_vehicle_valuation_from_rc

result = get_vehicle_valuation_from_rc(
    rc_number="DL08AB1234",
    api_token="your_surepass_api_token",
    current_ex_showroom=650000,
    market_listings_mean=425000  # Optional
)

if result['success']:
    print("RC Details:", result['rc_details'])
    print("Valuation:", result['valuation'])
```

### Method 3: 🆕 Gemini AI-Powered IDV (Automatic)

```python
from gemini_idv_engine import calculate_idv_with_gemini

# Just provide RC number - Gemini finds everything else!
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

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| make | str | Yes | Vehicle manufacturer |
| model | str | Yes | Vehicle model |
| variant | str | No | Model variant |
| fuel_type | str | Yes | Petrol/Diesel/CNG/Electric |
| reg_date | str | Yes | Registration date (YYYY-MM-DD) |
| rto_code | str | Yes | RTO registration code |
| city | str | Yes | Current location |
| body_type | str | Yes | Hatchback/Sedan/SUV/Luxury |
| color | str | Yes | Vehicle color |
| owner_count | int | No | Number of owners (default: 1) |
| current_ex_showroom | float | Yes | Current new model price |
| market_listings_mean | float | No | Average market listing price |
| odometer | int | No | Odometer reading (auto-calculated if missing) |

## Output Structure

```json
{
  "fair_market_retail_value": 389250.50,
  "dealer_purchase_price": 342425.45,
  "metadata": {
    "vehicle_age_years": 5.75,
    "estimated_odometer": 45000,
    "base_depreciation_percent": 42.0,
    "book_value": 350000.00,
    "regional_adjustment_factor": 1.0
  }
}
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_valuation.py
python3 test_rc_integration.py
python3 example_usage.py
```

## Key Logic Highlights

### Depreciation Grid
- < 6 months: 5%
- 1-2 years: 18%
- 3-4 years: 30%
- 5-6 years: 40%
- 8+ years: 60%

### Regional Adjustments
- **NCR Diesel Ban**: 25% penalty for 8+ year diesel vehicles
- **South India Premium**: 12% increase for KA/TS/TN/KL/AP
- **Coastal Corrosion**: 4% penalty for Mumbai/Chennai/Kolkata (5+ years)

### Dealer Margins
- Hatchback: 10% + ₹8,000 refurb
- Sedan/SUV: 12% + ₹15,000 refurb
- Luxury: 15% + ₹25,000 refurb

## RC API Configuration

To use the Surepass RC API integration:

1. Sign up at [Surepass](https://surepass.io)
2. Get your API token
3. Use it in the `get_vehicle_valuation_from_rc()` function

```python
API_TOKEN = "your_surepass_api_token_here"
```

## Project Structure

```
resale calculaator/
├── vehicle_valuation.py      # Core valuation engine (6 layers)
├── rc_api_integration.py     # Surepass RC API client
├── test_valuation.py         # Valuation engine tests
├── test_rc_integration.py    # RC API integration tests
├── example_usage.py          # Usage examples
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

## License

Proprietary - Automotive FinTech Solution
