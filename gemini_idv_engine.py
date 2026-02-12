from google import genai
from google.genai import types
import json
import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

class GeminiIDVEngine:
    """
    Gemini-powered IDV calculation engine
    Automatically finds historical on-road prices and calculates IDV
    """
    
    def __init__(self, gemini_api_key=None):
        self.api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        self.searchapi_key = os.getenv('SEARCHAPI_KEY')
        
        # Initialize new google.genai client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.0-flash'
        print(f"Using model: {self.model_name}")
    
    def calculate_idv_from_rc(self, rc_data):
        """
        Complete IDV calculation workflow using Gemini
        
        Args:
            rc_data: Raw RC API response
        
        Returns:
            dict: IDV calculation result with validation
        """
        
        # Step 1: Normalize vehicle data
        normalized_data = self._normalize_rc_data(rc_data)
        
        # Step 2: Check database cache first
        from database import ValuationDB
        db = ValuationDB()
        
        vehicle_make = normalized_data['maker_description'].replace(' INDIA LTD', '').replace(' LTD', '').replace(' INDIA', '').replace(' PVT', '').replace(' PRIVATE LIMITED', '').replace(' LIMITED', '').replace(' MOTOR', '').replace(' MOTORS', '').replace(' COMPANY', '').replace(' CO.', '').replace(' INC', '').replace(' CORPORATION', '').strip()
        vehicle_model = normalized_data['maker_model'].split()[0]  # Base model only
        manufacturing_year = normalized_data['manufacturing_date'][:4]
        city = normalized_data['city']
        
        # Check for exact match in database
        cached = db.get_exact_match_valuation(vehicle_make, vehicle_model, manufacturing_year, city)
        
        if cached:
            print(f"✅ CACHE HIT: Found {vehicle_make} {vehicle_model} {manufacturing_year} - NO API calls")
            # Update odometer and age based on current date
            if rc_data and 'manufacturing_date_formatted' in rc_data:
                try:
                    mfg_date_str = rc_data['manufacturing_date_formatted']
                    mfg_year, mfg_month = map(int, mfg_date_str.split('-'))
                    current_date = datetime.now()
                    age_years = current_date.year - mfg_year
                    age_months = current_date.month - mfg_month
                    if age_months < 0:
                        age_years -= 1
                        age_months += 12
                    total_months = age_years * 12 + age_months
                    cached['vehicle_age'] = f"{age_years} years {age_months} months"
                    cached['estimated_odometer'] = total_months * 1000
                except:
                    pass
            return cached
        
        print(f"❌ CACHE MISS: Calling SearchAPI + Gemini for {vehicle_make} {vehicle_model} {manufacturing_year}")
        
        # Step 3: Create structured prompt for Gemini (with SearchAPI only if not cached)
        prompt = self._create_gemini_prompt(normalized_data, use_search=True)
        
        # Step 4: Get Gemini response
        gemini_response = self._call_gemini(prompt)
        
        # Step 5: Parse Gemini response
        idv_result = self._parse_gemini_response(gemini_response)
        
        # Step 6: Backend validation (20% rule) and age correction
        validated_result = self._validate_idv(idv_result, rc_data)
        
        # Add model name to result
        validated_result['ai_model'] = self.model_name
        
        # Save to database for future cache hits
        try:
            db.save_valuation('TEMP_RC', {'raw_data': rc_data}, validated_result)
            print(f"✅ Saved to database for future cache hits")
        except Exception as e:
            print(f"⚠️ Failed to save to database: {e}")
        
        return validated_result
    
    def _normalize_rc_data(self, rc_data):
        """Normalize RC API data for Gemini"""
        
        vehicle_category = rc_data.get('vehicle_category_description', '')
        vehicle_type = '2W' if any(x in vehicle_category.upper() for x in ['SCOOTER', 'MOTORCYCLE']) else '4W'
        
        city = rc_data.get('registered_at', '').split(',')[0].strip()
        if not city:
            address = rc_data.get('present_address', '')
            city = address.split(',')[0].strip() if ',' in address else address.strip()
        
        return {
            'vehicle_type': vehicle_type,
            'maker_description': rc_data.get('maker_description', ''),
            'maker_model': rc_data.get('maker_model', ''),
            'fuel_type': rc_data.get('fuel_type', ''),
            'cubic_capacity': rc_data.get('cubic_capacity', ''),
            'norms_type': rc_data.get('norms_type', ''),
            'manufacturing_date': rc_data.get('manufacturing_date_formatted', ''),
            'city': city,
            'vehicle_category': vehicle_category
        }
    
    def _search_market_prices(self, vehicle_model, city, year):
        """Search market prices using SearchAPI"""
        if not self.searchapi_key:
            return None
        
        try:
            # Extract base model name (remove variant details)
            base_model = vehicle_model.split()[0]  # e.g., "VIRTUS GT LINE" -> "VIRTUS"
            
            # Try specific query first
            query = f"{vehicle_model} {city} used car price {year}"
            response = requests.get(
                'https://www.searchapi.io/api/v1/search',
                params={'engine': 'google', 'q': query, 'api_key': self.searchapi_key}
            )
            
            data = response.json() if response.status_code == 200 else None
            
            # If no results, try simpler query with base model
            if data and len(data.get('organic_results', [])) < 3:
                query = f"{base_model} {city} used car price {year}"
                response = requests.get(
                    'https://www.searchapi.io/api/v1/search',
                    params={'engine': 'google', 'q': query, 'api_key': self.searchapi_key}
                )
                data = response.json() if response.status_code == 200 else None
            
            return data
        except:
            return None
    
    def _create_gemini_prompt(self, data, use_search=True):
        """Create structured prompt for Gemini with 6-layer valuation logic"""
        
        # Get market data from SearchAPI only if use_search is True
        market_context = ""
        if use_search:
            market_data = self._search_market_prices(
                data['maker_model'], 
                data['city'], 
                data['manufacturing_date'][:4]
            )
            
            if market_data and 'organic_results' in market_data:
                market_context = "\n\nREAL-TIME MARKET DATA (EXTRACT PRICES FROM THIS):\n"
                for result in market_data['organic_results'][:5]:
                    market_context += f"- {result.get('title', '')}: {result.get('snippet', '')}\n"
                market_context += "\nIMPORTANT: Extract ALL prices mentioned above (₹ or Rs. or Lakh) and calculate the median as market_listings_mean.\n"
        
        return f"""You are an Indian Used Vehicle Resale Valuation Engine with 6-Layer Architecture.

CRITICAL RULE:
Vehicle age MUST be calculated using manufacturing_date: {data['manufacturing_date']}
Do NOT use registration_date.

================================
VEHICLE DETAILS
================================

Vehicle Type: {data['vehicle_type']}
Manufacturer: {data['maker_description']}
Model: {data['maker_model']}
Fuel Type: {data['fuel_type']}
Engine Capacity: {data['cubic_capacity']} cc
BS Norms: {data['norms_type']}
Manufacturing Date: {data['manufacturing_date']}
City: {data['city']}
Category: {data['vehicle_category']}
{market_context}

================================
6-LAYER VALUATION LOGIC
================================

LAYER 1: DERIVED METRICS
- Calculate age from manufacturing_date to today ("X years Y months")
- Assume odometer: 1000 km/month × total months
- High usage (>15k km/year): +5% depreciation penalty
- Low usage (<6k km/year): -3% depreciation bonus

LAYER 2: BASE DEPRECIATION GRID
Apply standard depreciation based on age:
- < 6 months: 5%
- 6-12 months: 10%
- 1-2 years: 18%
- 2-3 years: 25%
- 3-4 years: 30%
- 4-5 years: 35%
- 5-6 years: 40%
- 6-7 years: 45%
- 7-8 years: 50%
- 8+ years: 60%

EV-SPECIFIC IDV CALCULATION:
For Electric Vehicles, apply formula:
IDV = (Base Price - Depreciation) + (Accessories Cost - Accessory Depreciation)
- Base Price: 85% of total (vehicle body, motor)
- Accessories: 15% of total (battery, charger, electronics)
- Accessory Depreciation: Base depreciation + 10% (battery degradation)
- Example: 3-year EV with ₹10L price:
  * Base: ₹8.5L × (1 - 0.30) = ₹5.95L
  * Accessories: ₹1.5L × (1 - 0.40) = ₹0.90L
  * IDV = ₹6.85L

Historical Price Logic:
- For vehicles ≤ 1 year: Use CURRENT EX-SHOWROOM PRICE ONLY
- For vehicles > 1 year: Find historical on-road price for manufacturing year {data['manufacturing_date'][:4]}
- If historical unknown: Estimated_Historical = Current_Price × (1 - 0.03 × Age_Years)

LAYER 3: MARKET INTELLIGENCE
- Discontinued models (Ford Ecosport, Honda Civic, etc.): -15% penalty
- New generation launched (Swift, Creta, etc.): -10% penalty for old gen
- Color NOT White/Silver/Grey: -2% penalty
- Owner Count Penalty: +4% depreciation per additional owner after first
  * 1st owner: No penalty
  * 2nd owner: -4% value
  * 3rd owner: -8% value
  * 4th owner: -12% value

LAYER 4: REGIONAL LOGIC
- NCR Diesel Ban ({data['city']}):
  * Age > 9.5 years + Diesel: Scrap value only
  * Age > 8 years + Diesel: -25% penalty
- South India Premium (KA/TS/TN/KL/AP): +12%
- Coastal Corrosion (Mumbai/Chennai/Kolkata, Age > 5 years): -4%

LAYER 5: VALUATION CONVERGENCE
- Find market listings mean from OLX/CarDekho/Droom
- Blend: Cars < 5 years: 70% Market / 30% Book Value
- Blend: Cars ≥ 5 years: 50% Market / 50% Book Value
- Apply 7% negotiation gap reduction

LAYER 6: DEALER ECONOMICS
- Dealer margin: Hatchback 10%, Sedan/SUV 12%, Luxury 15%
- Refurb cost: Hatchback ₹8k, Sedan ₹15k, Luxury ₹25k

================================
SEARCHAPI MARKET DATA (USE THIS)
================================

You have been provided REAL market data above.
DO NOT search Google yourself.
Use ONLY the SearchAPI results provided in REAL-TIME MARKET DATA section.

================================
AI LEARNING & REASONING
================================

Use the SearchAPI market data provided above to:

1. Extract prices from snippets
2. Calculate median of available listings
3. Apply 6-layer valuation logic
4. Use depreciation grid for base calculation
5. Adjust based on regional factors
6. Blend market data with book value

================================
YOUR TASK
================================

1. Find current ex-showroom price for "{data['maker_model']}"
2. Calculate vehicle age from {data['manufacturing_date']}
3. Apply Layer 2 depreciation grid
4. Apply Layer 3 market intelligence adjustments
5. Apply Layer 4 regional adjustments for {data['city']}
6. Find market listings mean (REQUIRED - search OLX/CarDekho)
7. Apply Layer 5 convergence blending
8. Calculate dealer purchase price (Layer 6)
9. CRITICAL: Calculate confidence_score (50-100%):
   - Start with 85% base confidence
   - Data quality: Complete vehicle details +10%, Missing data -15%
   - Price accuracy: Historical price found +10%, Estimated -5%
   - Market validation: 3+ listings +10%, 1-2 listings +5%, No listings -20%
   - Regional match: Exact city match +5%
   - MINIMUM: 50%, MAXIMUM: 100%

================================
OUTPUT JSON ONLY
================================

{{
  "vehicle_type": "{data['vehicle_type']}",
  "vehicle_make": "",
  "vehicle_model": "{data['maker_model']}",
  "variant": "",
  "manufacturing_year": "{data['manufacturing_date'][:4]}",
  "city_used_for_price": "{data['city']}",
  "current_ex_showroom": 0,
  "vehicle_age": "",
  "estimated_odometer": 0,
  "base_depreciation_percent": 0,
  "book_value": 0,
  "market_listings_mean": 0,
  "fair_market_retail_value": 0,
  "dealer_purchase_price": 0,
  "confidence_score": 0
}}

DO NOT output explanation. JSON ONLY."""
    
    def _call_gemini(self, prompt):
        """Call Gemini API with proper error handling and retry"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2
                    )
                )
                
                # Check for grounding metadata
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'grounding_metadata'):
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, 'web_search_queries'):
                            print(f"DEBUG: Grounding active - {len(metadata.web_search_queries)} searches")
                
                # Extract text from response
                if hasattr(response, 'text') and response.text:
                    print(f"DEBUG: Response text length: {len(response.text)}")
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                        if text:
                            print(f"DEBUG: Extracted text from parts, length: {len(text)}")
                            return text
                
                print(f"DEBUG: No text found in response")
                raise ValueError("Empty response from Gemini")
                    
            except Exception as e:
                error_msg = str(e)
                if 'Bad Gateway' in error_msg or '502' in error_msg or 'Network error' in error_msg:
                    if attempt < max_retries - 1:
                        print(f"DEBUG: Retry {attempt + 1}/{max_retries} after Bad Gateway error")
                        import time
                        time.sleep(retry_delay)
                        continue
                raise Exception(f"Gemini API error: {error_msg}")
        
        raise Exception("Gemini API error: Max retries exceeded")
    
    def _parse_gemini_response(self, response_text):
        """Parse Gemini JSON response"""
        try:
            # Check if response is empty
            if not response_text or not response_text.strip():
                raise ValueError("Empty response from Gemini")
            
            cleaned = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Check if cleaned response is empty
            if not cleaned:
                print(f"DEBUG: Response after cleaning is empty")
                print(f"DEBUG: Original response: {response_text}")
                raise ValueError("No JSON content after cleaning")
            
            parsed_data = json.loads(cleaned)
            
            numeric_fields = [
                'current_ex_showroom', 'estimated_odometer', 'base_depreciation_percent',
                'book_value', 'market_listings_mean', 'fair_market_retail_value',
                'dealer_purchase_price', 'confidence_score'
            ]
            
            for field in numeric_fields:
                if field in parsed_data:
                    try:
                        parsed_data[field] = float(parsed_data[field]) if parsed_data[field] else 0.0
                    except (ValueError, TypeError):
                        parsed_data[field] = 0.0
            
            return parsed_data
        
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON error at pos {e.pos}: {str(e)}")
            print(f"DEBUG: Response length: {len(response_text)}")
            print(f"DEBUG: First 500: {response_text[:500]}")
            print(f"DEBUG: Last 500: {response_text[-500:]}")
            raise Exception(f"Failed to parse Gemini response: {str(e)}")
        except Exception as e:
            print(f"DEBUG: Parse error: {str(e)}")
            print(f"DEBUG: Response text: {response_text}")
            raise Exception(f"Failed to parse Gemini response: {str(e)}")
    
    def _validate_idv(self, idv_result, rc_data=None):
        """Backend validation with 20% rule and age correction"""
        
        # Clean vehicle make - remove company suffixes
        if 'vehicle_make' in idv_result:
            make = idv_result['vehicle_make']
            make = make.replace(' INDIA LTD', '').replace(' LTD', '').replace(' INDIA', '')
            make = make.replace(' PVT', '').replace(' PRIVATE LIMITED', '').replace(' LIMITED', '')
            make = make.replace(' MOTOR', '').replace(' MOTORS', '').replace(' COMPANY', '')
            make = make.replace(' CO.', '').replace(' INC', '').replace(' CORPORATION', '')
            idv_result['vehicle_make'] = make.strip()
        
        # Separate model and variant
        if 'vehicle_model' in idv_result and 'variant' in idv_result:
            model = idv_result['vehicle_model']
            variant = idv_result['variant']
            
            # If variant is in model, remove it
            if variant and variant in model:
                model = model.replace(variant, '').strip()
                idv_result['vehicle_model'] = model
        
        # Recalculate age correctly from manufacturing_date_formatted
        if rc_data and 'manufacturing_date_formatted' in rc_data:
            try:
                mfg_date_str = rc_data['manufacturing_date_formatted']  # Format: "2017-12"
                print(f"DEBUG: Manufacturing date from RC: {mfg_date_str}")  # Debug log
                mfg_year, mfg_month = map(int, mfg_date_str.split('-'))
                
                current_date = datetime.now()
                current_year = current_date.year
                current_month = current_date.month
                
                # Calculate exact age
                age_years = current_year - mfg_year
                age_months = current_month - mfg_month
                
                if age_months < 0:
                    age_years -= 1
                    age_months += 12
                
                # Update manufacturing year to match calculated age
                idv_result['manufacturing_year'] = str(mfg_year)
                idv_result['vehicle_age'] = f"{age_years} years {age_months} months"
                
                # Correct odometer calculation
                total_months = age_years * 12 + age_months
                correct_odometer = total_months * 1000  # 1000 km per month
                idv_result['estimated_odometer'] = correct_odometer
                
                # Correct depreciation based on actual age
                total_months = age_years * 12 + age_months
                vehicle_type = idv_result.get('vehicle_type', '2W')
                
                # Apply 6-layer depreciation grid
                if total_months <= 6:
                    correct_depreciation = 5
                elif total_months <= 12:
                    correct_depreciation = 10
                elif total_months <= 24:
                    correct_depreciation = 18
                elif total_months <= 36:
                    correct_depreciation = 25
                elif total_months <= 48:
                    correct_depreciation = 30
                elif total_months <= 60:
                    correct_depreciation = 35
                elif total_months <= 72:
                    correct_depreciation = 40
                elif total_months <= 84:
                    correct_depreciation = 45
                elif total_months <= 96:
                    correct_depreciation = 50
                else:
                    correct_depreciation = 60
                
                # Update if Gemini got it wrong
                if idv_result.get('base_depreciation_percent') != correct_depreciation:
                    idv_result['base_depreciation_percent'] = correct_depreciation
                    
            except:
                pass
        
        # Ensure numeric values are properly handled
        fair_market = float(idv_result.get('fair_market_retail_value', 0) or 0)
        market_listings = float(idv_result.get('market_listings_mean', 0) or 0)
        
        if market_listings and market_listings > 0:
            difference = abs(fair_market - market_listings) / market_listings * 100
            
            if difference > 20:
                validation_status = "Manual Review Required"
                confidence_adjustment = -20
            else:
                validation_status = "Within Acceptable Range"
                confidence_adjustment = 0
            
            idv_result['difference_percent'] = round(difference, 2)
            idv_result['validation_status'] = validation_status
            # Keep Gemini's confidence, only apply minimum 50%
            idv_result['confidence_score'] = max(50, float(idv_result.get('confidence_score', 85)))
        else:
            idv_result['difference_percent'] = 0.0
            idv_result['validation_status'] = "No Market Data"
            # Keep Gemini's confidence, only apply minimum 50%
            idv_result['confidence_score'] = max(50, float(idv_result.get('confidence_score', 75)))
        
        return idv_result


def calculate_idv_with_gemini(rc_number, surepass_token, gemini_api_key=None):
    """
    Complete workflow: RC Number → IDV Calculation
    
    Args:
        rc_number: Vehicle registration number
        surepass_token: Surepass API token
        gemini_api_key: Gemini API key (optional, uses env var)
    
    Returns:
        dict: Complete IDV result
    """
    from rc_api_integration import RCAPIClient
    
    # Step 1: Fetch RC data
    rc_client = RCAPIClient(surepass_token)
    rc_details = rc_client.fetch_vehicle_details(rc_number)
    
    if not rc_details:
        return {
            'success': False,
            'error': 'Failed to fetch RC details'
        }
    
    # Step 2: Calculate IDV using Gemini
    try:
        gemini_engine = GeminiIDVEngine(gemini_api_key)
        idv_result = gemini_engine.calculate_idv_from_rc(rc_details['raw_data'])
        
        return {
            'success': True,
            'rc_details': rc_details,
            'idv_calculation': idv_result
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Example usage
if __name__ == '__main__':
    # Sample RC data
    sample_rc = {
        "maker_description": "HONDA MOTORCYCLE & SCOOTER INDIA PVT LTD",
        "maker_model": "ACTIVA 5G",
        "fuel_type": "PETROL",
        "cubic_capacity": "109.19",
        "norms_type": "BS4",
        "manufacturing_date_formatted": "2017-12",
        "vehicle_category_description": "Scooter(2WN)",
        "registered_at": "DELHI, Delhi",
        "present_address": "New Delhi, 110034"
    }
    
    engine = GeminiIDVEngine()
    result = engine.calculate_idv_from_rc(sample_rc)
    print(json.dumps(result, indent=2))
