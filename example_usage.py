"""
Example Usage: Vehicle Valuation Engine
Demonstrates both manual input and RC API integration
"""

import json
from vehicle_valuation import calculate_resale_value
from rc_api_integration import get_vehicle_valuation_from_rc

# ============================================================
# METHOD 1: Manual Vehicle Data Input
# ============================================================

def example_manual_valuation():
    """Example: Calculate valuation with manual vehicle data"""
    
    print("=" * 70)
    print("METHOD 1: MANUAL VEHICLE DATA INPUT")
    print("=" * 70)
    
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
    
    print("\nInput Vehicle Data:")
    print(json.dumps(vehicle_data, indent=2))
    
    result = calculate_resale_value(vehicle_data)
    
    print("\n" + "-" * 70)
    print("VALUATION RESULT")
    print("-" * 70)
    print(f"\nFair Market Retail Value: ₹{result['fair_market_retail_value']:,.2f}")
    print(f"Dealer Purchase Price:    ₹{result['dealer_purchase_price']:,.2f}")
    print(f"\nVehicle Age:              {result['metadata']['vehicle_age_years']} years")
    print(f"Estimated Odometer:       {result['metadata']['estimated_odometer']:,} km")
    print(f"Base Depreciation:        {result['metadata']['base_depreciation_percent']}%")
    print(f"Book Value:               ₹{result['metadata']['book_value']:,.2f}")
    print(f"Regional Adjustment:      {result['metadata']['regional_adjustment_factor']}x")
    print("\n")


# ============================================================
# METHOD 2: RC API Integration (Automatic Data Fetch)
# ============================================================

def example_rc_api_valuation():
    """Example: Calculate valuation using RC API"""
    
    print("=" * 70)
    print("METHOD 2: RC API INTEGRATION (AUTO-FETCH)")
    print("=" * 70)
    
    # Configuration
    RC_NUMBER = "DL08AB1234"
    API_TOKEN = "your_surepass_api_token_here"  # Replace with actual token
    CURRENT_EX_SHOWROOM = 75000  # Honda Activa current price
    MARKET_LISTINGS_MEAN = 45000  # Optional
    
    print(f"\nFetching RC details for: {RC_NUMBER}")
    print("Note: Replace API_TOKEN with your actual Surepass token\n")
    
    # Uncomment below to test with real API
    """
    result = get_vehicle_valuation_from_rc(
        rc_number=RC_NUMBER,
        api_token=API_TOKEN,
        current_ex_showroom=CURRENT_EX_SHOWROOM,
        market_listings_mean=MARKET_LISTINGS_MEAN
    )
    
    if result['success']:
        print("-" * 70)
        print("RC DETAILS")
        print("-" * 70)
        rc = result['rc_details']
        print(f"RC Number:        {rc['rc_number']}")
        print(f"Make:             {rc['make']}")
        print(f"Model:            {rc['model']}")
        print(f"Fuel Type:        {rc['fuel_type']}")
        print(f"Registration:     {rc['reg_date']}")
        print(f"City:             {rc['city']}")
        print(f"Color:            {rc['color']}")
        print(f"Owner Count:      {rc['owner_count']}")
        
        print("\n" + "-" * 70)
        print("VALUATION RESULT")
        print("-" * 70)
        val = result['valuation']
        print(f"\nFair Market Retail Value: ₹{val['fair_market_retail_value']:,.2f}")
        print(f"Dealer Purchase Price:    ₹{val['dealer_purchase_price']:,.2f}")
        print(f"\nVehicle Age:              {val['metadata']['vehicle_age_years']} years")
        print(f"Book Value:               ₹{val['metadata']['book_value']:,.2f}")
    else:
        print(f"Error: {result['error']}")
    """
    
    print("(API integration ready - add your token to test)")
    print("\n")


# ============================================================
# METHOD 3: Batch Valuation
# ============================================================

def example_batch_valuation():
    """Example: Calculate valuations for multiple vehicles"""
    
    print("=" * 70)
    print("METHOD 3: BATCH VALUATION")
    print("=" * 70)
    
    vehicles = [
        {
            'name': 'Maruti Swift (Delhi)',
            'data': {
                'make': 'Maruti Suzuki', 'model': 'Swift', 'fuel_type': 'Petrol',
                'reg_date': '2019-03-15', 'rto_code': 'DL3C', 'city': 'Delhi',
                'body_type': 'Hatchback', 'color': 'White', 'owner_count': 1,
                'current_ex_showroom': 650000, 'market_listings_mean': 425000
            }
        },
        {
            'name': 'Hyundai Creta (Bangalore)',
            'data': {
                'make': 'Hyundai', 'model': 'Creta', 'fuel_type': 'Petrol',
                'reg_date': '2020-01-15', 'rto_code': 'KA01', 'city': 'Bangalore',
                'body_type': 'SUV', 'color': 'White', 'owner_count': 1,
                'current_ex_showroom': 1500000, 'market_listings_mean': 1100000
            }
        },
        {
            'name': 'Honda City Diesel (Delhi - 8+ years)',
            'data': {
                'make': 'Honda', 'model': 'City', 'fuel_type': 'Diesel',
                'reg_date': '2013-06-10', 'rto_code': 'DL8C', 'city': 'Delhi',
                'body_type': 'Sedan', 'color': 'Silver', 'owner_count': 2,
                'current_ex_showroom': 1200000, 'market_listings_mean': 250000
            }
        }
    ]
    
    print("\nCalculating valuations for 3 vehicles...\n")
    
    for vehicle in vehicles:
        result = calculate_resale_value(vehicle['data'])
        print(f"{vehicle['name']}")
        print(f"  Retail Value:  ₹{result['fair_market_retail_value']:>10,.0f}")
        print(f"  Dealer Price:  ₹{result['dealer_purchase_price']:>10,.0f}")
        print(f"  Age:           {result['metadata']['vehicle_age_years']:>10.1f} years")
        print()


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("VEHICLE VALUATION ENGINE - USAGE EXAMPLES")
    print("=" * 70 + "\n")
    
    # Run examples
    example_manual_valuation()
    example_rc_api_valuation()
    example_batch_valuation()
    
    print("=" * 70)
    print("For more examples, see test_valuation.py and test_rc_integration.py")
    print("=" * 70 + "\n")
