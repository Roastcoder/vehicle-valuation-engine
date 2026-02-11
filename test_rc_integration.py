import json
from rc_api_integration import RCAPIClient

def test_rc_parsing():
    """Test RC API response parsing with sample data"""
    
    # Sample RC API response (from your example)
    sample_response = {
        "rc_number": "DL08AB1234",
        "fit_up_to": "2032-12-15",
        "registration_date": "2018-01-20",
        "owner_name": "R***N K****R",
        "present_address": "New Delhi, 110034",
        "vehicle_category": "2WN",
        "maker_description": "HONDA MOTORCYCLE & SCOOTER INDIA PVT LTD",
        "maker_model": "ACTIVA 5G",
        "body_type": "SCOOTER",
        "fuel_type": "PETROL",
        "color": "BLACK",
        "financed": False,
        "insurance_upto": "2025-12-20",
        "manufacturing_date_formatted": "2017-12",
        "registered_at": "DELHI, Delhi",
        "owner_number": "1"
    }
    
    # Initialize client (no token needed for parsing test)
    client = RCAPIClient("test_token")
    
    # Parse the response
    parsed_data = client._parse_rc_response(sample_response)
    
    print("=" * 60)
    print("RC API PARSING TEST")
    print("=" * 60)
    print("\nParsed Vehicle Data:")
    print(json.dumps(parsed_data, indent=2, default=str))
    print("\n✓ Parsing successful")
    
    return parsed_data


def test_complete_workflow_mock():
    """Test complete workflow with mock RC data"""
    from vehicle_valuation import calculate_resale_value
    
    # Simulate parsed RC data
    rc_data = {
        'rc_number': 'DL08AB1234',
        'make': 'Honda',
        'model': 'ACTIVA 5G',
        'variant': '',
        'fuel_type': 'Petrol',
        'reg_date': '2018-01-20',
        'rto_code': 'DL08',
        'city': 'Delhi',
        'body_type': 'Hatchback',
        'color': 'Black',
        'owner_count': 1
    }
    
    # Prepare valuation input
    valuation_input = {
        'make': rc_data['make'],
        'model': rc_data['model'],
        'variant': rc_data['variant'],
        'fuel_type': rc_data['fuel_type'],
        'reg_date': rc_data['reg_date'],
        'rto_code': rc_data['rto_code'],
        'city': rc_data['city'],
        'body_type': rc_data['body_type'],
        'color': rc_data['color'],
        'owner_count': rc_data['owner_count'],
        'current_ex_showroom': 75000,  # Current Honda Activa price
        'market_listings_mean': 45000
    }
    
    # Calculate valuation
    result = calculate_resale_value(valuation_input)
    
    print("\n" + "=" * 60)
    print("COMPLETE WORKFLOW TEST (Mock Data)")
    print("=" * 60)
    print("\nRC Details:")
    print(json.dumps(rc_data, indent=2))
    print("\nValuation Result:")
    print(json.dumps(result, indent=2))
    print("\n✓ Workflow successful")


def test_car_example():
    """Test with a car example"""
    from vehicle_valuation import calculate_resale_value
    
    # Simulate car RC data
    rc_data = {
        'rc_number': 'KA01MN5678',
        'make': 'Maruti Suzuki',
        'model': 'Swift',
        'variant': 'VXI',
        'fuel_type': 'Petrol',
        'reg_date': '2019-06-15',
        'rto_code': 'KA01',
        'city': 'Bangalore',
        'body_type': 'Hatchback',
        'color': 'White',
        'owner_count': 1
    }
    
    valuation_input = {
        **rc_data,
        'current_ex_showroom': 650000,
        'market_listings_mean': 425000,
        'odometer': 48000
    }
    
    result = calculate_resale_value(valuation_input)
    
    print("\n" + "=" * 60)
    print("CAR VALUATION TEST (Maruti Swift)")
    print("=" * 60)
    print("\nRC Details:")
    print(json.dumps(rc_data, indent=2))
    print("\nValuation Result:")
    print(json.dumps(result, indent=2))
    print("\n✓ Car valuation successful")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("RC API INTEGRATION - TEST SUITE")
    print("=" * 60 + "\n")
    
    test_rc_parsing()
    test_complete_workflow_mock()
    test_car_example()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    print("\nNote: To test with real API, update API_TOKEN in rc_api_integration.py")
