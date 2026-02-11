#!/usr/bin/env python3
"""Quick test with your Surepass token"""

import os
from rc_api_integration import get_vehicle_valuation_from_rc

# Load token
SUREPASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NjM5ODg5MiwianRpIjoiMjdiNjdiNWEtZjkyZC00YTZmLTk2NmMtMDhhZjc4ZjAwNmI2IiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiZGV2LmZpbm9uZXN0aW5kaWFAc3VyZXBhc3MuaW8iLCJuYmYiOjE3NjYzOTg4OTIsImV4cCI6MjM5NzExODg5MiwiZW1haWwiOiJmaW5vbmVzdGluZGlhQHN1cmVwYXNzLmlvIiwidGVuYW50X2lkIjoibWFpbiIsInVzZXJfY2xhaW1zIjp7InNjb3BlcyI6WyJ1c2VyIl19fQ.dl1S5S3OxNs3hwxkwtLhcTAN6CmIlYa_hg4yOl5ASlg"

print("Testing RC API with your token...")
print("=" * 60)

result = get_vehicle_valuation_from_rc(
    rc_number="DL08AB1234",
    api_token=SUREPASS_TOKEN,
    current_ex_showroom=650000
)

if result['success']:
    print("✅ SUCCESS!")
    print(f"\nVehicle: {result['rc_details']['make']} {result['rc_details']['model']}")
    print(f"Fair Market Value: ₹{result['valuation']['fair_market_retail_value']:,.2f}")
    print(f"Dealer Price: ₹{result['valuation']['dealer_purchase_price']:,.2f}")
else:
    print(f"❌ Error: {result['error']}")
