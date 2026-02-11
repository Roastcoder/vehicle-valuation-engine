#!/bin/bash
# Production startup script

echo "Starting Vehicle Valuation API (Production Mode)"
gunicorn --bind 0.0.0.0:8080 --workers 4 --timeout 120 api_server:app
