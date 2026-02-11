"""
Test Gemini IDV Engine
Note: Requires GEMINI_API_KEY environment variable
"""

import json
import os
from gemini_idv_engine import GeminiIDVEngine

def test_gemini_idv_2w():
    """Test Gemini IDV for 2-wheeler"""
    
    print("=" * 70)
    print("Test: Gemini IDV Engine - 2-Wheeler (Honda Activa)")
    print("=" * 70)
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  GEMINI_API_KEY not set. Skipping test.")
        print("Set environment variable: export GEMINI_API_KEY='your_key'")
        return
    
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
    
    try:
        engine = GeminiIDVEngine()
        result = engine.calculate_idv_from_rc(rc_data)
        
        print("\n✓ Gemini Response:")
        print(json.dumps(result, indent=2))
        print("\n✓ Test Passed")
        
    except Exception as e:
        print(f"\n✗ Test Failed: {str(e)}")


def test_gemini_idv_4w():
    """Test Gemini IDV for 4-wheeler"""
    
    print("\n" + "=" * 70)
    print("Test: Gemini IDV Engine - 4-Wheeler (Maruti Swift)")
    print("=" * 70)
    
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  GEMINI_API_KEY not set. Skipping test.")
        return
    
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
    
    try:
        engine = GeminiIDVEngine()
        result = engine.calculate_idv_from_rc(rc_data)
        
        print("\n✓ Gemini Response:")
        print(json.dumps(result, indent=2))
        print("\n✓ Test Passed")
        
    except Exception as e:
        print(f"\n✗ Test Failed: {str(e)}")


def test_workflow_explanation():
    """Explain the complete workflow"""
    
    print("\n" + "=" * 70)
    print("GEMINI IDV ENGINE - WORKFLOW")
    print("=" * 70)
    
    print("""
Step 1: User Enters RC Number
        ↓
Step 2: Call RC API (Surepass)
        ↓
Step 3: Normalize Vehicle Data
        - Extract make, model, fuel, CC, BS norms
        - Detect vehicle type (2W/4W)
        - Extract manufacturing date
        ↓
Step 4: Send Structured Prompt to Gemini
        - Request historical on-road price
        - Request exact variant identification
        - Request market median estimate
        ↓
Step 5: Gemini Finds Historical On-Road Price
        - Searches for year-specific price
        - Matches exact variant
        - Estimates if only ex-showroom available
        ↓
Step 6: Gemini Calculates IDV
        - Calculates vehicle age from mfg date
        - Applies correct depreciation (2W/4W)
        - Computes IDV
        ↓
Step 7: Backend Validates 20% Rule
        - Compares calculated IDV vs market median
        - If difference > 20%: Manual Review Required
        - If difference ≤ 20%: Within Acceptable Range
        ↓
Step 8: Final IDV Response
        - Returns complete JSON with validation status
    """)
    
    print("=" * 70)


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("GEMINI IDV ENGINE - TEST SUITE")
    print("=" * 70 + "\n")
    
    test_workflow_explanation()
    test_gemini_idv_2w()
    test_gemini_idv_4w()
    
    print("\n" + "=" * 70)
    print("TESTS COMPLETED")
    print("=" * 70)
    print("\nNote: To run with real API, set GEMINI_API_KEY environment variable")
    print("Example: export GEMINI_API_KEY='your_gemini_api_key'")
