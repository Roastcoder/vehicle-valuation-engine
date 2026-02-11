#!/usr/bin/env python3
"""
Test Gemini-Powered IDV Calculation
Run this after starting the API server
"""

import requests
import json
import os

def test_gemini_idv():
    """Test Gemini IDV endpoint"""
    
    print("=" * 70)
    print("GEMINI-POWERED IDV CALCULATION TEST")
    print("=" * 70)
    print()
    
    # API endpoint
    url = "http://localhost:5000/api/v1/idv/gemini"
    
    # Test data
    payload = {
        "rc_number": "DL08AB1234"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print()
    
    print("Calling Gemini AI...")
    print("  → Fetching RC details from RTO")
    print("  → Finding historical on-road price")
    print("  → Calculating vehicle age from manufacturing date")
    print("  → Applying depreciation")
    print("  → Calculating IDV")
    print("  → Validating with market data")
    print()
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ SUCCESS!")
                print()
                print("Response:")
                print(json.dumps(result, indent=2))
                
                # Display summary
                if 'idv_calculation' in result:
                    idv = result['idv_calculation']
                    print()
                    print("=" * 70)
                    print("IDV SUMMARY")
                    print("=" * 70)
                    print(f"Vehicle: {idv.get('vehicle_make')} {idv.get('vehicle_model')}")
                    print(f"Manufacturing Year: {idv.get('manufacturing_year')}")
                    print(f"Age: {idv.get('vehicle_age')}")
                    print(f"Original On-Road Price: ₹{idv.get('original_on_road_price', 0):,}")
                    print(f"Depreciation: {idv.get('depreciation_percent')}%")
                    print(f"Calculated IDV: ₹{idv.get('calculated_idv', 0):,}")
                    print(f"Validation: {idv.get('validation_status')}")
                    print(f"Confidence: {idv.get('confidence_score')}%")
                    print("=" * 70)
            else:
                print("❌ FAILED")
                print(f"Error: {result.get('error')}")
        else:
            print("❌ HTTP ERROR")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("Make sure the API server is running on http://localhost:5000")
        print("Start it with: python3 api_server.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()


if __name__ == '__main__':
    # Check environment variables
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  WARNING: GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your_key'")
        print()
    
    if not os.getenv('SUREPASS_API_TOKEN'):
        print("⚠️  WARNING: SUREPASS_API_TOKEN not set")
        print("Set it with: export SUREPASS_API_TOKEN='your_token'")
        print()
    
    test_gemini_idv()
