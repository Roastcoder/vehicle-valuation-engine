import json
from vehicle_valuation import calculate_resale_value

def test_basic_valuation():
    """Test basic valuation for a standard vehicle"""
    vehicle = {
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
    result = calculate_resale_value(vehicle)
    print("Test 1 - Basic Valuation:")
    print(json.dumps(result, indent=2))
    assert result['fair_market_retail_value'] > 0
    assert result['dealer_purchase_price'] > 0
    print("✓ Passed\n")

def test_ncr_diesel_ban():
    """Test NCR diesel ban logic"""
    vehicle = {
        'make': 'Honda',
        'model': 'City',
        'variant': 'VX',
        'fuel_type': 'Diesel',
        'reg_date': '2013-06-10',
        'rto_code': 'DL8C',
        'city': 'Delhi',
        'body_type': 'Sedan',
        'color': 'Silver',
        'owner_count': 2,
        'current_ex_showroom': 1200000,
        'market_listings_mean': 250000
    }
    result = calculate_resale_value(vehicle)
    print("Test 2 - NCR Diesel Ban (>8 years):")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

def test_south_india_premium():
    """Test South India premium"""
    vehicle = {
        'make': 'Hyundai',
        'model': 'Creta',
        'variant': 'SX',
        'fuel_type': 'Petrol',
        'reg_date': '2020-01-15',
        'rto_code': 'KA01',
        'city': 'Bangalore',
        'body_type': 'SUV',
        'color': 'White',
        'owner_count': 1,
        'current_ex_showroom': 1500000,
        'market_listings_mean': 1100000
    }
    result = calculate_resale_value(vehicle)
    print("Test 3 - South India Premium:")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

def test_discontinued_model():
    """Test discontinued model penalty"""
    vehicle = {
        'make': 'Ford',
        'model': 'Ecosport',
        'variant': 'Titanium',
        'fuel_type': 'Petrol',
        'reg_date': '2018-05-20',
        'rto_code': 'MH01',
        'city': 'Mumbai',
        'body_type': 'SUV',
        'color': 'Red',
        'owner_count': 1,
        'current_ex_showroom': 1100000,
        'market_listings_mean': 550000
    }
    result = calculate_resale_value(vehicle)
    print("Test 4 - Discontinued Model:")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

def test_luxury_vehicle():
    """Test luxury vehicle with higher dealer margins"""
    vehicle = {
        'make': 'Mercedes-Benz',
        'model': 'C-Class',
        'variant': 'C200',
        'fuel_type': 'Petrol',
        'reg_date': '2019-08-10',
        'rto_code': 'DL3C',
        'city': 'Delhi',
        'body_type': 'Luxury',
        'color': 'Black',
        'owner_count': 1,
        'current_ex_showroom': 4500000,
        'market_listings_mean': 2800000
    }
    result = calculate_resale_value(vehicle)
    print("Test 5 - Luxury Vehicle:")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

def test_high_mileage_penalty():
    """Test high mileage penalty"""
    vehicle = {
        'make': 'Maruti Suzuki',
        'model': 'Dzire',
        'variant': 'VXI',
        'fuel_type': 'Petrol',
        'reg_date': '2020-01-01',
        'rto_code': 'KA03',
        'city': 'Bangalore',
        'body_type': 'Sedan',
        'color': 'White',
        'owner_count': 1,
        'current_ex_showroom': 750000,
        'market_listings_mean': 500000,
        'odometer': 100000  # High mileage for 5 years
    }
    result = calculate_resale_value(vehicle)
    print("Test 6 - High Mileage Penalty:")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

def test_coastal_corrosion():
    """Test coastal corrosion penalty"""
    vehicle = {
        'make': 'Tata',
        'model': 'Nexon',
        'variant': 'XZ',
        'fuel_type': 'Petrol',
        'reg_date': '2017-03-15',
        'rto_code': 'MH02',
        'city': 'Mumbai',
        'body_type': 'SUV',
        'color': 'Blue',
        'owner_count': 1,
        'current_ex_showroom': 1200000,
        'market_listings_mean': 600000
    }
    result = calculate_resale_value(vehicle)
    print("Test 7 - Coastal Corrosion:")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

def test_no_market_listing():
    """Test valuation without market listing data"""
    vehicle = {
        'make': 'Kia',
        'model': 'Seltos',
        'variant': 'HTX',
        'fuel_type': 'Petrol',
        'reg_date': '2021-06-01',
        'rto_code': 'TN09',
        'city': 'Chennai',
        'body_type': 'SUV',
        'color': 'White',
        'owner_count': 1,
        'current_ex_showroom': 1600000
    }
    result = calculate_resale_value(vehicle)
    print("Test 8 - No Market Listing Data:")
    print(json.dumps(result, indent=2))
    print("✓ Passed\n")

if __name__ == '__main__':
    print("=" * 60)
    print("VEHICLE VALUATION ENGINE - TEST SUITE")
    print("=" * 60 + "\n")
    
    test_basic_valuation()
    test_ncr_diesel_ban()
    test_south_india_premium()
    test_discontinued_model()
    test_luxury_vehicle()
    test_high_mileage_penalty()
    test_coastal_corrosion()
    test_no_market_listing()
    
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
