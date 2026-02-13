"""
Flask API Wrapper for Vehicle Valuation Engine
Deploy as a REST API service
"""

from flask import Flask, request, jsonify, render_template
from vehicle_valuation import calculate_resale_value
from rc_api_integration import get_vehicle_valuation_from_rc
from database import ValuationDB
import os
import json

app = Flask(__name__)

# Run database migration on startup
try:
    import sqlite3
    if os.path.exists('valuations.db'):
        conn = sqlite3.connect('valuations.db')
        cursor = conn.cursor()
        try:
            cursor.execute('ALTER TABLE valuations ADD COLUMN vehicle_variant TEXT')
            conn.commit()
        except:
            pass  # Column already exists
        conn.close()
except:
    pass

db = ValuationDB()

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


@app.route('/api/v1/rc/details', methods=['POST'])
def get_rc_details():
    """
    Get RC details only (no valuation)
    
    Request Body:
    {
        "rc_number": "MH46CV4464"
    }
    """
    try:
        from rc_api_integration import RCAPIClient
        
        data = request.get_json()
        
        if 'rc_number' not in data:
            return jsonify({'success': False, 'error': 'Missing required field: rc_number'}), 400
        
        rc_number = data['rc_number'].upper()
        surepass_token = data.get('surepass_token', SUREPASS_API_TOKEN)
        
        if not surepass_token:
            return jsonify({'success': False, 'error': 'Surepass API token not configured'}), 401
        
        rc_client = RCAPIClient(surepass_token)
        rc_details = rc_client.fetch_vehicle_details(rc_number)
        
        if not rc_details:
            return jsonify({'success': False, 'error': 'Failed to fetch RC details'}), 500
        
        return jsonify({'success': True, 'rc_details': rc_details})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/idv/gemini', methods=['POST'])
def idv_with_gemini():
    """
    Calculate IDV using Gemini AI (auto-finds historical prices)
    1. Call RC API to get vehicle details
    2. Check database for matching vehicle (make, model, variant, year)
    3. If found: return cached valuation with recalculated odometer
    4. If not found: call Gemini API for full valuation
    
    Request Body:
    {
        "rc_number": "DL08AB1234"
    }
    
    Query Parameters:
    - skip_cache=true : Force fresh calculation, skip database cache
    """
    try:
        from gemini_idv_engine import calculate_idv_with_gemini
        from rc_api_integration import RCAPIClient
        from datetime import datetime
        
        data = request.get_json()
        skip_cache = request.args.get('skip_cache', 'false').lower() == 'true'
        
        if 'rc_number' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: rc_number'
            }), 400
        
        rc_number = data['rc_number'].upper()
        surepass_token = data.get('surepass_token', SUREPASS_API_TOKEN)
        
        if not surepass_token:
            return jsonify({
                'success': False,
                'error': 'Surepass API token not configured'
            }), 401
        
        # STEP 1: Call RC API to get vehicle details
        rc_client = RCAPIClient(surepass_token)
        rc_details = rc_client.fetch_vehicle_details(rc_number)
        
        if not rc_details:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch RC details'
            }), 500
        
        raw_data = rc_details.get('raw_data', {})
        vehicle_make = raw_data.get('maker_description', '').replace(' INDIA LTD', '').replace(' LTD', '').replace(' INDIA', '').strip()
        vehicle_model = raw_data.get('maker_model', '')
        manufacturing_year = raw_data.get('manufacturing_date_formatted', '')[:4]
        
        # STEP 2: Check database for matching vehicle details (make, model, year) - skip if skip_cache=true
        existing = None if skip_cache else db.get_valuation_by_vehicle_details(vehicle_make, vehicle_model, vehicle_model, manufacturing_year)
        
        if existing:
            # STEP 3: Found in database - recalculate only odometer and age
            try:
                mfg_date_str = raw_data.get('manufacturing_date_formatted', '')
                if mfg_date_str:
                    mfg_year, mfg_month = map(int, mfg_date_str.split('-'))
                    current_date = datetime.now()
                    age_years = current_date.year - mfg_year
                    age_months = current_date.month - mfg_month
                    if age_months < 0:
                        age_years -= 1
                        age_months += 12
                    
                    total_months = age_years * 12 + age_months
                    estimated_odometer = total_months * 1000
                    vehicle_age = f"{age_years} years {age_months} months"
                else:
                    estimated_odometer = existing.get('estimated_odometer')
                    vehicle_age = existing.get('vehicle_age')
            except:
                estimated_odometer = existing.get('estimated_odometer')
                vehicle_age = existing.get('vehicle_age')
            
            # Get similar vehicles
            similar_vehicles = db.get_similar_vehicles(
                vehicle_model=vehicle_model,
                manufacturing_year=manufacturing_year,
                fuel_type=raw_data.get('fuel_type'),
                state=raw_data.get('registered_at', '').split(',')[-1].strip()
            )
            
            return jsonify({
                'success': True,
                'source': 'database',
                'cached': True,
                'rc_details': {
                    'rc_number': rc_number,
                    'raw_data': raw_data
                },
                'idv_calculation': {
                    'vehicle_make': existing.get('vehicle_make'),
                    'vehicle_model': existing.get('vehicle_model'),
                    'variant': existing.get('vehicle_variant'),
                    'manufacturing_year': existing.get('manufacturing_year'),
                    'vehicle_age': vehicle_age,
                    'owner_count': existing.get('owner_count'),
                    'fair_market_retail_value': existing.get('fair_market_retail_value'),
                    'dealer_purchase_price': existing.get('dealer_purchase_price'),
                    'current_ex_showroom': existing.get('current_ex_showroom'),
                    'estimated_odometer': estimated_odometer,
                    'base_depreciation_percent': existing.get('base_depreciation_percent'),
                    'book_value': existing.get('book_value'),
                    'market_listings_mean': existing.get('market_listings_mean'),
                    'confidence_score': existing.get('confidence_score'),
                    'ai_model': existing.get('ai_model'),
                    'city_used_for_price': existing.get('city')
                },
                'similar_vehicles': similar_vehicles
            })
        
        # STEP 4: Not in database - call Gemini API for full valuation
        gemini_key = data.get('gemini_api_key', GEMINI_API_KEY)
        
        if not gemini_key:
            return jsonify({
                'success': False,
                'error': 'Gemini API key not configured'
            }), 401
        
        result = calculate_idv_with_gemini(
            rc_number=rc_number,
            surepass_token=surepass_token,
            gemini_api_key=gemini_key
        )
        
        # Save to database if successful
        if result.get('success') and result.get('idv_calculation'):
            db.save_valuation(
                rc_number=rc_number,
                rc_details=result['rc_details'],
                idv_calculation=result['idv_calculation']
            )
            result['source'] = 'api'
            result['cached'] = False
            
            # Get similar vehicles
            idv_calc = result['idv_calculation']
            similar_vehicles = db.get_similar_vehicles(
                vehicle_model=idv_calc.get('vehicle_model'),
                manufacturing_year=idv_calc.get('manufacturing_year'),
                fuel_type=raw_data.get('fuel_type'),
                state=raw_data.get('registered_at', '').split(',')[-1].strip()
            )
            result['similar_vehicles'] = similar_vehicles
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/valuations/<rc_number>', methods=['GET'])
def get_valuation_history(rc_number):
    """Get valuation history for RC number"""
    try:
        history = db.get_valuation_history(rc_number)
        return jsonify({
            'success': True,
            'rc_number': rc_number,
            'count': len(history),
            'valuations': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/valuations/recent', methods=['GET'])
def get_recent_valuations():
    """Get recent valuations"""
    try:
        limit = request.args.get('limit', 10, type=int)
        recent = db.get_recent_valuations(limit)
        return jsonify({
            'success': True,
            'count': len(recent),
            'valuations': recent
        })
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
