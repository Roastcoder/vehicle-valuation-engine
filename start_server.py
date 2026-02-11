#!/usr/bin/env python3
"""Start API server on port 5001"""

import os
os.environ['SUREPASS_API_TOKEN'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NjM5ODg5MiwianRpIjoiMjdiNjdiNWEtZjkyZC00YTZmLTk2NmMtMDhhZjc4ZjAwNmI2IiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiZGV2LmZpbm9uZXN0aW5kaWFAc3VyZXBhc3MuaW8iLCJuYmYiOjE3NjYzOTg4OTIsImV4cCI6MjM5NzExODg5MiwiZW1haWwiOiJmaW5vbmVzdGluZGlhQHN1cmVwYXNzLmlvIiwidGVuYW50X2lkIjoibWFpbiIsInVzZXJfY2xhaW1zIjp7InNjb3BlcyI6WyJ1c2VyIl19fQ.dl1S5S3OxNs3hwxkwtLhcTAN6CmIlYa_hg4yOl5ASlg"

from flask import Flask, request, jsonify, render_template
from vehicle_valuation import calculate_resale_value
from rc_api_integration import get_vehicle_valuation_from_rc

app = Flask(__name__)

SUREPASS_API_TOKEN = os.getenv('SUREPASS_API_TOKEN', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Vehicle Valuation API',
        'version': '1.0.0',
        'endpoints': {
            'health': 'GET /health',
            'manual_valuation': 'POST /api/v1/valuation/manual',
            'rc_valuation': 'POST /api/v1/valuation/rc',
            'idv_gemini': 'POST /api/v1/idv/gemini'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Vehicle Valuation Engine'})

@app.route('/api/v1/valuation/manual', methods=['POST'])
def manual_valuation():
    try:
        vehicle_data = request.get_json()
        result = calculate_resale_value(vehicle_data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/valuation/rc', methods=['POST'])
def rc_valuation():
    try:
        data = request.get_json()
        api_token = data.get('api_token', SUREPASS_API_TOKEN)
        
        result = get_vehicle_valuation_from_rc(
            rc_number=data['rc_number'],
            api_token=api_token,
            current_ex_showroom=data['current_ex_showroom'],
            market_listings_mean=data.get('market_listings_mean')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/idv/gemini', methods=['POST'])
def idv_with_gemini():
    try:
        from gemini_idv_engine import calculate_idv_with_gemini
        data = request.get_json()
        
        result = calculate_idv_with_gemini(
            rc_number=data['rc_number'],
            surepass_token=data.get('surepass_token', SUREPASS_API_TOKEN),
            gemini_api_key=data.get('gemini_api_key', GEMINI_API_KEY)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Vehicle Valuation API Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health                    - Health check")
    print("  POST /api/v1/valuation/manual   - Manual valuation")
    print("  POST /api/v1/valuation/rc       - RC API valuation")
    print("  POST /api/v1/idv/gemini         - IDV with Gemini AI")
    print("\nStarting server on http://localhost:5001")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
