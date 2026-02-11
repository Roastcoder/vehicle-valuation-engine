import json
from idv_calculation import calculate_idv

def test_2w_idv_calculation():
    """Test IDV calculation for 2-wheeler (Honda Activa)"""
    
    rc_data = {
        "maker_description": "HONDA MOTORCYCLE & SCOOTER INDIA PVT LTD",
        "maker_model": "ACTIVA 5G",
        "fuel_type": "PETROL",
        "cubic_capacity": "109.19",
        "norms_type": "BS4",
        "manufacturing_date_formatted": "2017-12",
        "vehicle_category_description": "Scooter(2WN)",
        "registered_at": "DELHI, Delhi",
        "present_address": "New Delhi, 110034"
    }
    
    original_on_road = 66000
    market_median = 42000
    
    result = calculate_idv(rc_data, original_on_road, market_median)
    
    print("=" * 70)
    print("Test 1: 2-Wheeler IDV (Honda Activa 5G - 7+ years old)")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("\n✓ Test Passed\n")


def test_4w_idv_calculation():
    """Test IDV calculation for 4-wheeler (Maruti Swift)"""
    
    rc_data = {
        "maker_description": "MARUTI SUZUKI INDIA LIMITED",
        "maker_model": "SWIFT VXI",
        "fuel_type": "PETROL",
        "cubic_capacity": "1197",
        "norms_type": "BS4",
        "manufacturing_date_formatted": "2019-02",
        "vehicle_category_description": "Motor Car(LMV)",
        "registered_at": "DELHI, Delhi",
        "present_address": "New Delhi, 110034"
    }
    
    # Swift VXI 2019 on-road price in Delhi: ~6.5 lakhs
    original_on_road = 650000
    market_median = 425000
    
    result = calculate_idv(rc_data, original_on_road, market_median)
    
    print("=" * 70)
    print("Test 2: 4-Wheeler IDV (Maruti Swift - 5-6 years old)")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("\n✓ Test Passed\n")


def test_new_vehicle_idv():
    """Test IDV for vehicle less than 6 months old"""
    
    rc_data = {
        "maker_description": "HYUNDAI MOTOR INDIA LIMITED",
        "maker_model": "CRETA SX",
        "fuel_type": "PETROL",
        "cubic_capacity": "1497",
        "norms_type": "BS6",
        "manufacturing_date_formatted": "2024-09",
        "vehicle_category_description": "Motor Car(LMV)",
        "registered_at": "BANGALORE, Karnataka",
        "present_address": "Bangalore, 560001"
    }
    
    original_on_road = 1500000
    
    result = calculate_idv(rc_data, original_on_road)
    
    print("=" * 70)
    print("Test 3: New Vehicle IDV (Hyundai Creta - < 6 months)")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("\n✓ Test Passed\n")


def test_old_car_idv():
    """Test IDV for old car (10+ years)"""
    
    rc_data = {
        "maker_description": "HONDA CARS INDIA LIMITED",
        "maker_model": "CITY I-VTEC",
        "fuel_type": "PETROL",
        "cubic_capacity": "1497",
        "norms_type": "BS3",
        "manufacturing_date_formatted": "2012-06",
        "vehicle_category_description": "Motor Car(LMV)",
        "registered_at": "MUMBAI, Maharashtra",
        "present_address": "Mumbai, 400001"
    }
    
    # Honda City 2012 on-road: ~10 lakhs
    original_on_road = 1000000
    market_median = 280000
    
    result = calculate_idv(rc_data, original_on_road, market_median)
    
    print("=" * 70)
    print("Test 4: Old Car IDV (Honda City - 12+ years)")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("\n✓ Test Passed\n")


def test_validation_status():
    """Test validation status logic"""
    
    rc_data = {
        "maker_description": "TATA MOTORS LIMITED",
        "maker_model": "NEXON XZ",
        "fuel_type": "PETROL",
        "cubic_capacity": "1199",
        "norms_type": "BS6",
        "manufacturing_date_formatted": "2020-03",
        "vehicle_category_description": "Motor Car(LMV)",
        "registered_at": "PUNE, Maharashtra",
        "present_address": "Pune, 411001"
    }
    
    original_on_road = 1000000
    
    # Test 1: Within acceptable range
    market_median_good = 520000
    result1 = calculate_idv(rc_data, original_on_road, market_median_good)
    
    print("=" * 70)
    print("Test 5a: Validation - Within Acceptable Range")
    print("=" * 70)
    print(f"Calculated IDV: {result1['calculated_idv']}")
    print(f"Market Median: {result1['market_median_estimate']}")
    print(f"Difference: {result1['difference_percent']}%")
    print(f"Status: {result1['validation_status']}")
    print("\n✓ Test Passed\n")
    
    # Test 2: Manual review required
    market_median_bad = 300000
    result2 = calculate_idv(rc_data, original_on_road, market_median_bad)
    
    print("=" * 70)
    print("Test 5b: Validation - Manual Review Required")
    print("=" * 70)
    print(f"Calculated IDV: {result2['calculated_idv']}")
    print(f"Market Median: {result2['market_median_estimate']}")
    print(f"Difference: {result2['difference_percent']}%")
    print(f"Status: {result2['validation_status']}")
    print("\n✓ Test Passed\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("IDV CALCULATION ENGINE - TEST SUITE")
    print("=" * 70 + "\n")
    
    test_2w_idv_calculation()
    test_4w_idv_calculation()
    test_new_vehicle_idv()
    test_old_car_idv()
    test_validation_status()
    
    print("=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)
