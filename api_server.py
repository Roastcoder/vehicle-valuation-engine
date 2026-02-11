"""
Flask API Wrapper for Vehicle Valuation Engine
Deploy as a REST API service
"""

from flask import Flask, request, jsonify, render_template
from vehicle_valuation import calculate_resale_value
from rc_api_integration import get_vehicle_valuation_from_rc
import os

app = Flask(__name__)

# Load API tokens from environment variables
SUREPASS_API_TOKEN = os.getenv('SUREPASS_API_TOKEN', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')


@app.route('/', methods=['GET'])
def home():
    """Landing page"""
    return render_template('index.html')


@app.route('/gemini', methods=['GET'])
def gemini_ui():
    """Gemini IDV Calculator UI"""
    return render_template('gemini_idv.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Vehicle Valuation Engine',
        'version': '1.0.0'
    })


@app.route('/api/v1/valuation/manual', methods=['POST'])
def manual_valuation():
    """
    Calculate valuation with manual vehicle data
    
    Request Body:
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
    }
    """
    try:
        vehicle_data = request.get_json()
        
        # Validate required fields
        required_fields = ['make', 'model', 'fuel_type', 'reg_date', 'rto_code', 
                          'city', 'body_type', 'color', 'current_ex_showroom']
        
        missing_fields = [field for field in required_fields if field not in vehicle_data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Calculate valuation
        result = calculate_resale_value(vehicle_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/valuation/rc', methods=['POST'])
def rc_valuation():
    """
    Calculate valuation using RC number (auto-fetch from RTO)
    
    Request Body:
    {
        "rc_number": "DL08AB1234",
        "current_ex_showroom": 650000,
        "market_listings_mean": 425000
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'rc_number' not in data or 'current_ex_showroom' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: rc_number, current_ex_showroom'
            }), 400
        
        # Check API token
        api_token = data.get('api_token', SUREPASS_API_TOKEN)
        if not api_token:
            return jsonify({
                'success': False,
                'error': 'API token not configured. Set SUREPASS_API_TOKEN environment variable.'
            }), 401
        
        # Fetch and calculate
        result = get_vehicle_valuation_from_rc(
            rc_number=data['rc_number'],
            api_token=api_token,
            current_ex_showroom=data['current_ex_showroom'],
            market_listings_mean=data.get('market_listings_mean')
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/valuation/batch', methods=['POST'])
def batch_valuation():
    """
    Calculate valuations for multiple vehicles
    
    Request Body:
    {
        "vehicles": [
            {
                "make": "Maruti Suzuki",
                "model": "Swift",
                ...
            },
            {
                "make": "Hyundai",
                "model": "Creta",
                ...
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if 'vehicles' not in data or not isinstance(data['vehicles'], list):
            return jsonify({
                'success': False,
                'error': 'Invalid request. Expected "vehicles" array.'
            }), 400
        
        results = []
        for idx, vehicle_data in enumerate(data['vehicles']):
            try:
                result = calculate_resale_value(vehicle_data)
                results.append({
                    'index': idx,
                    'success': True,
                    'data': result
                })
            except Exception as e:
                results.append({
                    'index': idx,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/idv/calculate', methods=['POST'])
def calculate_idv_endpoint():
    """
    Calculate IDV (Insured Declared Value) for motor insurance
    
    Request Body:
    {
        "rc_data": { /* RC API response */ },
        "original_on_road_price": 66000,
        "market_median_estimate": 42000
    }
    """
    try:
        from idv_calculation import calculate_idv
        
        data = request.get_json()
        
        if 'rc_data' not in data or 'original_on_road_price' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: rc_data, original_on_road_price'
            }), 400
        
        result = calculate_idv(
            rc_data=data['rc_data'],
            original_on_road_price=data['original_on_road_price'],
            market_median_estimate=data.get('market_median_estimate')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/idv/rc', methods=['POST'])
def idv_from_rc():
    """
    Calculate IDV using RC number (auto-fetch from RTO)
    
    Request Body:
    {
        "rc_number": "DL08AB1234",
        "original_on_road_price": 66000,
        "market_median_estimate": 42000
    }
    """
    try:
        from idv_calculation import get_idv_from_rc
        
        data = request.get_json()
        
        if 'rc_number' not in data or 'original_on_road_price' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: rc_number, original_on_road_price'
            }), 400
        
        api_token = data.get('api_token', SUREPASS_API_TOKEN)
        if not api_token:
            return jsonify({
                'success': False,
                'error': 'API token not configured'
            }), 401
        
        result = get_idv_from_rc(
            rc_number=data['rc_number'],
            api_token=api_token,
            original_on_road_price=data['original_on_road_price'],
            market_median_estimate=data.get('market_median_estimate')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/idv/gemini', methods=['POST'])
def idv_with_gemini():
    """
    Calculate IDV using Gemini AI (auto-finds historical prices)
    
    Request Body:
    {
        "rc_number": "DL08AB1234"
    }
    """
    try:
        from gemini_idv_engine import calculate_idv_with_gemini
        
        data = request.get_json()
        
        if 'rc_number' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: rc_number'
            }), 400
        
        surepass_token = data.get('surepass_token', SUREPASS_API_TOKEN)
        gemini_key = data.get('gemini_api_key', GEMINI_API_KEY)
        
        if not surepass_token:
            return jsonify({
                'success': False,
                'error': 'Surepass API token not configured'
            }), 401
        
        if not gemini_key:
            return jsonify({
                'success': False,
                'error': 'Gemini API key not configured'
            }), 401
        
        result = calculate_idv_with_gemini(
            rc_number=data['rc_number'],
            surepass_token=surepass_token,
            gemini_api_key=gemini_key
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Development server
    print("=" * 60)
    print("Vehicle Valuation API Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health                    - Health check")
    print("  POST /api/v1/valuation/manual   - Manual valuation")
    print("  POST /api/v1/valuation/rc       - RC API valuation")
    print("  POST /api/v1/valuation/batch    - Batch valuation")
    print("  POST /api/v1/idv/calculate      - IDV calculation")
    print("  POST /api/v1/idv/rc             - IDV from RC API")
    print("  POST /api/v1/idv/gemini         - IDV with Gemini AI (auto-price)")
    print("\nStarting server on http://localhost:8080")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
