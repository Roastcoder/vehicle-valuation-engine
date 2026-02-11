#!/bin/bash

# API Test Script
# Test the Vehicle Valuation API endpoints

API_URL="http://localhost:5000"

echo "=========================================="
echo "Vehicle Valuation API - Test Script"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -X GET "${API_URL}/health" \
  -H "Content-Type: application/json" \
  -s | python3 -m json.tool
echo ""
echo ""

# Test 2: Manual Valuation
echo "Test 2: Manual Valuation (Maruti Swift)"
echo "----------------------------------------"
curl -X POST "${API_URL}/api/v1/valuation/manual" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Maruti Suzuki",
    "model": "Swift",
    "variant": "VXI",
    "fuel_type": "Petrol",
    "reg_date": "2019-03-15",
    "rto_code": "DL3C",
    "city": "Delhi",
    "body_type": "Hatchback",
    "color": "White",
    "owner_count": 1,
    "current_ex_showroom": 650000,
    "market_listings_mean": 425000,
    "odometer": 45000
  }' \
  -s | python3 -m json.tool
echo ""
echo ""

# Test 3: RC API Valuation (requires API token)
echo "Test 3: RC API Valuation"
echo "------------------------"
echo "Note: This requires SUREPASS_API_TOKEN environment variable"
echo "Uncomment the curl command below to test with real API"
echo ""
# curl -X POST "${API_URL}/api/v1/valuation/rc" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "rc_number": "DL08AB1234",
#     "current_ex_showroom": 75000,
#     "market_listings_mean": 45000
#   }' \
#   -s | python3 -m json.tool
echo ""

# Test 4: Batch Valuation
echo "Test 4: Batch Valuation (3 vehicles)"
echo "-------------------------------------"
curl -X POST "${API_URL}/api/v1/valuation/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "fuel_type": "Petrol",
        "reg_date": "2019-03-15",
        "rto_code": "DL3C",
        "city": "Delhi",
        "body_type": "Hatchback",
        "color": "White",
        "current_ex_showroom": 650000,
        "market_listings_mean": 425000
      },
      {
        "make": "Hyundai",
        "model": "Creta",
        "fuel_type": "Petrol",
        "reg_date": "2020-01-15",
        "rto_code": "KA01",
        "city": "Bangalore",
        "body_type": "SUV",
        "color": "White",
        "current_ex_showroom": 1500000,
        "market_listings_mean": 1100000
      },
      {
        "make": "Honda",
        "model": "City",
        "fuel_type": "Diesel",
        "reg_date": "2013-06-10",
        "rto_code": "DL8C",
        "city": "Delhi",
        "body_type": "Sedan",
        "color": "Silver",
        "owner_count": 2,
        "current_ex_showroom": 1200000,
        "market_listings_mean": 250000
      }
    ]
  }' \
  -s | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "All Tests Completed"
echo "=========================================="
