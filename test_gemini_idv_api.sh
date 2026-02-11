#!/bin/bash

# Test Gemini-Powered IDV Calculation
# Just provide RC number - Gemini finds everything else!

echo "=========================================="
echo "GEMINI-POWERED IDV CALCULATION TEST"
echo "=========================================="
echo ""

# Configuration
API_URL="http://localhost:5000/api/v1/idv/gemini"
RC_NUMBER="DL08AB1234"

echo "Testing with RC Number: $RC_NUMBER"
echo ""
echo "Calling Gemini AI to:"
echo "  1. Fetch RC details from RTO"
echo "  2. Find historical on-road price"
echo "  3. Calculate vehicle age from manufacturing date"
echo "  4. Apply depreciation"
echo "  5. Calculate IDV"
echo "  6. Validate with market data"
echo ""
echo "Please wait..."
echo ""

# Make API call
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"rc_number\": \"$RC_NUMBER\"
  }" \
  -s | python3 -m json.tool

echo ""
echo "=========================================="
echo "TEST COMPLETED"
echo "=========================================="
