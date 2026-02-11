from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

def calculate_idv(rc_data, original_on_road_price, market_median_estimate=None):
    """
    Calculate IDV (Insured Declared Value) for motor insurance
    Uses manufacturing_date_formatted for age calculation (NOT registration_date)
    
    Args:
        rc_data: Parsed RC API response
        original_on_road_price: Year-specific on-road price
        market_median_estimate: Optional market median for validation
    
    Returns:
        dict: IDV calculation result
    """
    
    # Extract data
    maker_desc = rc_data.get('maker_description', '')
    maker_model = rc_data.get('maker_model', '')
    fuel_type = rc_data.get('fuel_type', '')
    cubic_capacity = rc_data.get('cubic_capacity', '')
    norms_type = rc_data.get('norms_type', '')
    mfg_date = rc_data.get('manufacturing_date_formatted', '')
    vehicle_category = rc_data.get('vehicle_category_description', '')
    registered_at = rc_data.get('registered_at', '')
    owner_count = int(rc_data.get('owner_number', 1))  # Extract owner count
    
    # Detect vehicle type
    is_electric = fuel_type.upper() in ['ELECTRIC', 'EV', 'BATTERY']
    vehicle_type = '2W' if any(x in vehicle_category.upper() for x in ['SCOOTER', 'MOTORCYCLE']) else '4W'
    
    # Extract make
    make = maker_desc.split()[0] if maker_desc else 'Unknown'
    
    # Extract city
    city = registered_at.split(',')[0].strip() if ',' in registered_at else registered_at.strip()
    
    # Extract manufacturing year
    mfg_year = mfg_date.split('-')[0] if mfg_date else ''
    
    # Calculate vehicle age from manufacturing date
    if mfg_date:
        mfg_datetime = datetime.strptime(mfg_date, '%Y-%m')
        current_date = datetime.now()
        age_delta = relativedelta(current_date, mfg_datetime)
        age_years = age_delta.years + age_delta.months / 12
        vehicle_age = f"{age_delta.years} years {age_delta.months} months"
    else:
        age_years = 0
        vehicle_age = "Unknown"
    
    # Apply depreciation based on vehicle type
    if vehicle_type == '2W':
        if age_years < 0.5:
            depreciation = 0.05
        elif age_years < 1:
            depreciation = 0.15
        elif age_years < 2:
            depreciation = 0.20
        elif age_years < 3:
            depreciation = 0.30
        elif age_years < 4:
            depreciation = 0.40
        elif age_years < 5:
            depreciation = 0.50
        elif age_years < 7:
            depreciation = 0.60
        else:
            depreciation = 0.65
    else:  # 4W
        if age_years < 0.5:
            depreciation = 0.05
        elif age_years < 1:
            depreciation = 0.15
        elif age_years < 2:
            depreciation = 0.20
        elif age_years < 3:
            depreciation = 0.30
        elif age_years < 4:
            depreciation = 0.40
        elif age_years < 5:
            depreciation = 0.50
        elif age_years < 7:
            depreciation = 0.55
        elif age_years < 10:
            depreciation = 0.65
        else:
            depreciation = 0.70
    
    # EV-specific IDV calculation: IDV = (MSP - Depreciation) + (Accessories - Accessory Depreciation)
    if is_electric:
        # For EVs, assume 15% of price is accessories (battery, charger, electronics)
        base_price = original_on_road_price * 0.85
        accessories_cost = original_on_road_price * 0.15
        
        # Higher depreciation on EV accessories (battery degradation)
        accessory_depreciation = min(depreciation + 0.10, 0.80)  # +10% extra, max 80%
        
        # IDV = (Base Price - Depreciation) + (Accessories - Accessory Depreciation)
        base_idv = base_price * (1 - depreciation)
        accessories_idv = accessories_cost * (1 - accessory_depreciation)
        calculated_idv = base_idv + accessories_idv
    else:
        # Standard IDV calculation for ICE vehicles
        calculated_idv = original_on_road_price * (1 - depreciation)
    
    # Apply owner count penalty: +4% depreciation per additional owner after first
    if owner_count > 1:
        owner_penalty = (owner_count - 1) * 0.04
        calculated_idv = calculated_idv * (1 - owner_penalty)
    
    # Validation
    if market_median_estimate:
        difference = abs(calculated_idv - market_median_estimate) / market_median_estimate * 100
        validation_status = "Manual Review Required" if difference > 20 else "Within Acceptable Range"
        confidence_score = max(50, 100 - difference)
    else:
        difference = 0
        validation_status = "No Market Data"
        confidence_score = max(50, 85)
    
    # Build variant string
    variant = f"{maker_model}"
    if cubic_capacity:
        variant += f" {cubic_capacity}cc"
    if norms_type:
        variant += f" {norms_type}"
    
    return {
        'vehicle_type': vehicle_type,
        'vehicle_make': make,
        'vehicle_model': maker_model,
        'variant': variant,
        'manufacturing_year': mfg_year,
        'city_used_for_price': city,
        'owner_count': owner_count,
        'original_on_road_price': round(original_on_road_price, 2),
        'vehicle_age': vehicle_age,
        'depreciation_percent': round(depreciation * 100, 2),
        'calculated_idv': round(calculated_idv, 2),
        'market_median_estimate': round(market_median_estimate, 2) if market_median_estimate else None,
        'difference_percent': round(difference, 2) if market_median_estimate else None,
        'validation_status': validation_status,
        'confidence_score': round(confidence_score, 2)
    }


def get_idv_from_rc(rc_number, api_token, original_on_road_price, market_median_estimate=None):
    """
    Complete workflow: Fetch RC details and calculate IDV
    
    Args:
        rc_number: Vehicle registration number
        api_token: Surepass API token
        original_on_road_price: Year-specific on-road price
        market_median_estimate: Optional market median
    
    Returns:
        dict: Complete IDV calculation result
    """
    from rc_api_integration import RCAPIClient
    
    client = RCAPIClient(api_token)
    rc_details = client.fetch_vehicle_details(rc_number)
    
    if not rc_details:
        return {
            'success': False,
            'error': 'Failed to fetch RC details'
        }
    
    # Use raw_data for IDV calculation
    raw_data = rc_details.get('raw_data', {})
    
    idv_result = calculate_idv(raw_data, original_on_road_price, market_median_estimate)
    
    return {
        'success': True,
        'rc_details': rc_details,
        'idv_calculation': idv_result
    }


# Example usage
if __name__ == '__main__':
    # Sample RC data (Honda Activa 5G from your example)
    sample_rc_data = {
        "rc_number": "DL08AB1234",
        "registration_date": "2018-01-20",
        "maker_description": "HONDA MOTORCYCLE & SCOOTER INDIA PVT LTD",
        "maker_model": "ACTIVA 5G",
        "body_type": "SCOOTER",
        "fuel_type": "PETROL",
        "color": "BLACK",
        "cubic_capacity": "109.19",
        "norms_type": "BS4",
        "manufacturing_date_formatted": "2017-12",
        "registered_at": "DELHI, Delhi",
        "present_address": "New Delhi, 110034",
        "vehicle_category_description": "Scooter(2WN)",
        "owner_number": "1"
    }
    
    # Original on-road price for Honda Activa 5G BS4 in Delhi (Dec 2017)
    # Approximate: Ex-showroom ~60,000 + RTO/Insurance ~6,000 = ~66,000
    original_on_road = 66000
    
    # Market median (optional - current used market price)
    market_median = 42000
    
    result = calculate_idv(sample_rc_data, original_on_road, market_median)
    
    print(json.dumps(result, indent=2))
