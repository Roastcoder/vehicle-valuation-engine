"""
IDV Calculation Examples
Demonstrates motor insurance IDV calculation using manufacturing date
"""

import json
from idv_calculation import calculate_idv, get_idv_from_rc

print("=" * 70)
print("IDV CALCULATION ENGINE - USAGE EXAMPLES")
print("=" * 70)
print()

# ============================================================
# EXAMPLE 1: 2-Wheeler IDV (Honda Activa)
# ============================================================

print("Example 1: 2-Wheeler IDV Calculation")
print("-" * 70)

rc_data_2w = {
    "rc_number": "DL08AB1234",
    "maker_description": "HONDA MOTORCYCLE & SCOOTER INDIA PVT LTD",
    "maker_model": "ACTIVA 5G",
    "fuel_type": "PETROL",
    "cubic_capacity": "109.19",
    "norms_type": "BS4",
    "manufacturing_date_formatted": "2017-12",  # CRITICAL: Used for age calculation
    "registration_date": "2018-01-20",          # NOT used for depreciation
    "vehicle_category_description": "Scooter(2WN)",
    "registered_at": "DELHI, Delhi",
    "present_address": "New Delhi, 110034"
}

# Original on-road price in Delhi (Dec 2017)
# Ex-showroom: ~60,000 + RTO/Insurance: ~6,000 = 66,000
original_on_road_2w = 66000

# Current market median (optional)
market_median_2w = 42000

result_2w = calculate_idv(rc_data_2w, original_on_road_2w, market_median_2w)

print("\nInput:")
print(f"  Vehicle: {result_2w['vehicle_make']} {result_2w['vehicle_model']}")
print(f"  Manufacturing Date: 2017-12")
print(f"  Original On-Road Price: ₹{original_on_road_2w:,}")
print(f"  Market Median: ₹{market_median_2w:,}")

print("\nOutput:")
print(f"  Vehicle Age: {result_2w['vehicle_age']}")
print(f"  Depreciation: {result_2w['depreciation_percent']}%")
print(f"  Calculated IDV: ₹{result_2w['calculated_idv']:,.2f}")
print(f"  Validation: {result_2w['validation_status']}")
print(f"  Confidence: {result_2w['confidence_score']}%")
print()

# ============================================================
# EXAMPLE 2: 4-Wheeler IDV (Maruti Swift)
# ============================================================

print("Example 2: 4-Wheeler IDV Calculation")
print("-" * 70)

rc_data_4w = {
    "maker_description": "MARUTI SUZUKI INDIA LIMITED",
    "maker_model": "SWIFT VXI",
    "fuel_type": "PETROL",
    "cubic_capacity": "1197",
    "norms_type": "BS4",
    "manufacturing_date_formatted": "2019-02",
    "registration_date": "2019-03-15",
    "vehicle_category_description": "Motor Car(LMV)",
    "registered_at": "DELHI, Delhi",
    "present_address": "New Delhi, 110034"
}

original_on_road_4w = 650000
market_median_4w = 425000

result_4w = calculate_idv(rc_data_4w, original_on_road_4w, market_median_4w)

print("\nInput:")
print(f"  Vehicle: {result_4w['vehicle_make']} {result_4w['vehicle_model']}")
print(f"  Manufacturing Date: 2019-02")
print(f"  Original On-Road Price: ₹{original_on_road_4w:,}")
print(f"  Market Median: ₹{market_median_4w:,}")

print("\nOutput:")
print(f"  Vehicle Age: {result_4w['vehicle_age']}")
print(f"  Depreciation: {result_4w['depreciation_percent']}%")
print(f"  Calculated IDV: ₹{result_4w['calculated_idv']:,.2f}")
print(f"  Validation: {result_4w['validation_status']}")
print(f"  Confidence: {result_4w['confidence_score']}%")
print()

# ============================================================
# EXAMPLE 3: New Vehicle (< 6 months)
# ============================================================

print("Example 3: New Vehicle IDV (< 6 months)")
print("-" * 70)

rc_data_new = {
    "maker_description": "HYUNDAI MOTOR INDIA LIMITED",
    "maker_model": "CRETA SX",
    "fuel_type": "PETROL",
    "cubic_capacity": "1497",
    "norms_type": "BS6",
    "manufacturing_date_formatted": "2024-09",
    "vehicle_category_description": "Motor Car(LMV)",
    "registered_at": "BANGALORE, Karnataka"
}

original_on_road_new = 1500000

result_new = calculate_idv(rc_data_new, original_on_road_new)

print("\nInput:")
print(f"  Vehicle: {result_new['vehicle_make']} {result_new['vehicle_model']}")
print(f"  Manufacturing Date: 2024-09")
print(f"  Original On-Road Price: ₹{original_on_road_new:,}")

print("\nOutput:")
print(f"  Vehicle Age: {result_new['vehicle_age']}")
print(f"  Depreciation: {result_new['depreciation_percent']}%")
print(f"  Calculated IDV: ₹{result_new['calculated_idv']:,.2f}")
print()

# ============================================================
# EXAMPLE 4: Old Vehicle (10+ years)
# ============================================================

print("Example 4: Old Vehicle IDV (10+ years)")
print("-" * 70)

rc_data_old = {
    "maker_description": "HONDA CARS INDIA LIMITED",
    "maker_model": "CITY I-VTEC",
    "fuel_type": "PETROL",
    "cubic_capacity": "1497",
    "norms_type": "BS3",
    "manufacturing_date_formatted": "2012-06",
    "vehicle_category_description": "Motor Car(LMV)",
    "registered_at": "MUMBAI, Maharashtra"
}

original_on_road_old = 1000000
market_median_old = 280000

result_old = calculate_idv(rc_data_old, original_on_road_old, market_median_old)

print("\nInput:")
print(f"  Vehicle: {result_old['vehicle_make']} {result_old['vehicle_model']}")
print(f"  Manufacturing Date: 2012-06")
print(f"  Original On-Road Price: ₹{original_on_road_old:,}")
print(f"  Market Median: ₹{market_median_old:,}")

print("\nOutput:")
print(f"  Vehicle Age: {result_old['vehicle_age']}")
print(f"  Depreciation: {result_old['depreciation_percent']}%")
print(f"  Calculated IDV: ₹{result_old['calculated_idv']:,.2f}")
print(f"  Validation: {result_old['validation_status']}")
print()

# ============================================================
# EXAMPLE 5: JSON Output Format
# ============================================================

print("Example 5: Complete JSON Output")
print("-" * 70)
print(json.dumps(result_2w, indent=2))
print()

print("=" * 70)
print("KEY POINTS:")
print("=" * 70)
print("✓ Age calculated from manufacturing_date_formatted (NOT registration_date)")
print("✓ Different depreciation rates for 2W vs 4W")
print("✓ Market validation with 20% threshold")
print("✓ Confidence score based on market difference")
print("=" * 70)
