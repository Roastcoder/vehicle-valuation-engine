#!/bin/bash
# Setup script for Vehicle Resale Calculator

echo "=========================================="
echo "Vehicle Resale Calculator - Setup"
echo "=========================================="
echo ""

# Set Surepass token
export SUREPASS_API_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NjM5ODg5MiwianRpIjoiMjdiNjdiNWEtZjkyZC00YTZmLTk2NmMtMDhhZjc4ZjAwNmI2IiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiZGV2LmZpbm9uZXN0aW5kaWFAc3VyZXBhc3MuaW8iLCJuYmYiOjE3NjYzOTg4OTIsImV4cCI6MjM5NzExODg5MiwiZW1haWwiOiJmaW5vbmVzdGluZGlhQHN1cmVwYXNzLmlvIiwidGVuYW50X2lkIjoibWFpbiIsInVzZXJfY2xhaW1zIjp7InNjb3BlcyI6WyJ1c2VyIl19fQ.dl1S5S3OxNs3hwxkwtLhcTAN6CmIlYa_hg4yOl5ASlg"

echo "✅ SUREPASS_API_TOKEN configured"
echo ""

# Check if Gemini key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo "   Then run: export GEMINI_API_KEY='your_key'"
    echo ""
else
    echo "✅ GEMINI_API_KEY configured"
    echo ""
fi

echo "=========================================="
echo "Ready to use!"
echo "=========================================="
echo ""
echo "Try these commands:"
echo "  python3 test_surepass.py          # Test RC API"
echo "  python3 api_server.py             # Start API server"
echo "  python3 run_gemini_test.py        # Test Gemini IDV"
echo ""
