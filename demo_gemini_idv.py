#!/usr/bin/env python3
"""
Complete End-to-End IDV Calculation Demo
RC Number → Gemini AI → IDV Result
"""

import os
import json

def demo_gemini_idv_workflow():
    """
    Demonstrate complete Gemini IDV workflow
    """
    
    print("=" * 70)
    print("GEMINI IDV CALCULATION - COMPLETE WORKFLOW DEMO")
    print("=" * 70)
    print()
    
    # Check API keys
    surepass_token = os.getenv('SUREPASS_API_TOKEN')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not surepass_token:
        print("⚠️  SUREPASS_API_TOKEN not set")
        print("This demo will use mock RC data instead")
        use_real_api = False
    else:
        use_real_api = True
    
    if not gemini_key:
        print("⚠️  GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your_key'")
        print()
        return
    
    print("✓ Configuration validated")
    print()
    
    # Workflow visualization
    print("WORKFLOW:")
    print("-" * 70)
    print("Step 1: User Enters RC Number")
    print("        ↓")
    print("Step 2: Call RC API (Surepass)")
    print("        ↓")
    print("Step 3: Normalize Vehicle Data")
    print("        ↓")
    print("Step 4: Send Structured Prompt to Gemini")
    print("        ↓")
    print("Step 5: Gemini Finds Historical On-Road Price")
    print("        ↓")
    print("Step 6: Gemini Calculates IDV")
    print("        ↓")
    print("Step 7: Backend Validates 20% Rule")
    print("        ↓")
    print("Step 8: Final IDV Response")
    print("-" * 70)
    print()
    
    # Example 1: Mock data (always works)
    print("EXAMPLE 1: Using Mock RC Data")
    print("-" * 70)
    
    from gemini_idv_engine import GeminiIDVEngine
    
    mock_rc_data = {
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
    
    print("\nInput RC Data:")
    print(f"  Vehicle: Honda ACTIVA 5G")
    print(f"  Manufacturing Date: 2017-12")
    print(f"  City: Delhi")
    print(f"  Type: 2-Wheeler (Scooter)")
    print()
    
    try:
        print("Calling Gemini AI...")
        engine = GeminiIDVEngine(gemini_key)
        result = engine.calculate_idv_from_rc(mock_rc_data)
        
        print("\n✅ IDV Calculation Result:")
        print(json.dumps(result, indent=2))
        
        print("\n📊 Summary:")
        print(f"  Vehicle: {result['vehicle_make']} {result['vehicle_model']}")
        print(f"  Age: {result['vehicle_age']}")
        print(f"  Original Price: ₹{result['original_on_road_price']:,}")
        print(f"  Depreciation: {result['depreciation_percent']}%")
        print(f"  Calculated IDV: ₹{result['calculated_idv']:,}")
        print(f"  Validation: {result['validation_status']}")
        print(f"  Confidence: {result['confidence_score']}%")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print()
    
    # Example 2: Real API (if configured)
    if use_real_api:
        print("\nEXAMPLE 2: Using Real RC API")
        print("-" * 70)
        print("Note: This requires a valid RC number and Surepass token")
        print("Uncomment the code below to test with real API")
        print()
        
        """
        from gemini_idv_engine import calculate_idv_with_gemini
        
        rc_number = "DL08AB1234"  # Replace with real RC number
        
        print(f"Fetching RC details for: {rc_number}")
        
        result = calculate_idv_with_gemini(
            rc_number=rc_number,
            surepass_token=surepass_token,
            gemini_api_key=gemini_key
        )
        
        if result['success']:
            print("\\n✅ Complete Result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\\n❌ Error: {result['error']}")
        """
    
    print()
    print("=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)
    print()
    print("Key Features:")
    print("  ✓ Automatic price discovery via Gemini AI")
    print("  ✓ Manufacturing date-based depreciation")
    print("  ✓ Market validation with 20% threshold")
    print("  ✓ Confidence scoring")
    print("  ✓ Zero manual input required")
    print()


if __name__ == '__main__':
    demo_gemini_idv_workflow()
