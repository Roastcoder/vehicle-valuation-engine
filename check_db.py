#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://ic8ss4g0s408wwss44gs4g4w.72.61.238.231.sslip.io"

def check_rc_in_db(rc_number):
    """Check if RC exists in database"""
    response = requests.get(f"{BASE_URL}/api/v1/rc/{rc_number}")
    return response.json()

def get_valuation_history(rc_number):
    """Get valuation history for RC"""
    response = requests.get(f"{BASE_URL}/api/v1/valuations/{rc_number}")
    return response.json()

if __name__ == "__main__":
    rc = sys.argv[1] if len(sys.argv) > 1 else "RJ13CD4810"
    
    print(f"Checking RC: {rc}")
    print("=" * 50)
    
    # Check RC details
    rc_data = check_rc_in_db(rc)
    print("\nRC Details:")
    print(rc_data)
    
    # Get valuation history
    history = get_valuation_history(rc)
    print("\nValuation History:")
    print(history)
