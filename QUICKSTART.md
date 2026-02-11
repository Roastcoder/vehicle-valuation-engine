# Quick Start Guide

## Setup (2 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Token (Optional)
```bash
cp config_template.py config.py
# Edit config.py and add your Surepass API token
```

## Usage Examples

### Example 1: Quick Valuation (Manual Input)
```python
from vehicle_valuation import calculate_resale_value

vehicle = {
    'make': 'Maruti Suzuki',
    'model': 'Swift',
    'fuel_type': 'Petrol',
    'reg_date': '2019-03-15',
    'rto_code': 'DL3C',
    'city': 'Delhi',
    'body_type': 'Hatchback',
    'color': 'White',
    'current_ex_showroom': 650000,
    'market_listings_mean': 425000
}

result = calculate_resale_value(vehicle)
print(f"Retail Value: ₹{result['fair_market_retail_value']:,.0f}")
print(f"Dealer Price: ₹{result['dealer_purchase_price']:,.0f}")
```

### Example 2: RC API Integration
```python
from rc_api_integration import get_vehicle_valuation_from_rc

result = get_vehicle_valuation_from_rc(
    rc_number="DL08AB1234",
    api_token="your_token",
    current_ex_showroom=650000
)

if result['success']:
    print(result['valuation'])
```

### Example 3: Run All Tests
```bash
python3 test_valuation.py
python3 test_rc_integration.py
python3 example_usage.py
```

## Key Features

✅ **6-Layer Valuation Logic**
- Derived metrics (age, mileage)
- Base depreciation (60% max)
- Market intelligence (discontinued models)
- Regional adjustments (NCR diesel ban, South premium)
- Market convergence (listing integration)
- Dealer economics (margins + refurb)

✅ **RC API Integration**
- Auto-fetch vehicle details from RTO
- Parse and map to valuation format
- Single function call for complete workflow

✅ **Regional Intelligence**
- NCR diesel ban (25% penalty for 8+ years)
- South India premium (12% increase)
- Coastal corrosion (4% penalty)

✅ **Dealer Pricing**
- Body-type specific margins
- Refurbishment cost deduction
- Ready for B2B integration

## Common Use Cases

### 1. Car Dealer Platform
```python
# Fetch RC → Calculate → Show offer
result = get_vehicle_valuation_from_rc(rc_number, token, ex_showroom)
dealer_offer = result['valuation']['dealer_purchase_price']
```

### 2. Loan Valuation
```python
# Calculate fair market value for loan approval
result = calculate_resale_value(vehicle_data)
loan_eligibility = result['fair_market_retail_value'] * 0.80  # 80% LTV
```

### 3. Insurance Valuation
```python
# Calculate IDV (Insured Declared Value)
result = calculate_resale_value(vehicle_data)
idv = result['metadata']['book_value']
```

## API Response Structure

### RC API Response
```json
{
  "success": true,
  "rc_details": {
    "rc_number": "DL08AB1234",
    "make": "Honda",
    "model": "ACTIVA 5G",
    "fuel_type": "Petrol",
    "reg_date": "2018-01-20",
    "city": "Delhi",
    "color": "Black",
    "owner_count": 1
  },
  "valuation": {
    "fair_market_retail_value": 42500.50,
    "dealer_purchase_price": 36250.45,
    "metadata": {...}
  }
}
```

## Troubleshooting

### Issue: API returns 401 Unauthorized
**Solution**: Check your API token in config.py

### Issue: Valuation seems too low
**Solution**: Verify current_ex_showroom price is accurate

### Issue: Regional adjustment not applied
**Solution**: Check RTO code format (e.g., "KA01" not "KA1")

## Next Steps

1. ✅ Test with sample data: `python3 example_usage.py`
2. ✅ Add your API token to `config.py`
3. ✅ Test RC API integration with real RC number
4. ✅ Integrate into your application

## Support

For issues or questions:
- Check test files for examples
- Review README.md for detailed documentation
- Verify input data format matches specifications
