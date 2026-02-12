from google import genai
from google.genai import types
import json
import os
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
        
        # Initialize new google.genai client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-3-pro-preview'
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
        vehicle_model = normalized_data['maker_model']
        manufacturing_year = normalized_data['manufacturing_date'][:4]
        
        cached = db.get_cached_valuation(vehicle_make, vehicle_model, '', manufacturing_year)
        
        if cached:
            print(f"DEBUG: Using cached valuation from database")
            # Recalculate only odometer based on registration date
            if rc_data and 'registration_date_formatted' in rc_data:
                try:
                    reg_date_str = rc_data['registration_date_formatted']
                    reg_year, reg_month = map(int, reg_date_str.split('-'))
                    current_date = datetime.now()
                    age_years = current_date.year - reg_year
                    age_months = current_date.month - reg_month
                    if age_months < 0:
                        age_years -= 1
                        age_months += 12
                    total_months = age_years * 12 + age_months
                    cached['estimated_odometer'] = total_months * 1000
                except:
                    pass
            return cached
        
        # Step 3: Create structured prompt for Gemini
        prompt = self._create_gemini_prompt(normalized_data)
        
        # Step 4: Get Gemini response
        gemini_response = self._call_gemini(prompt)
        
        # Step 5: Parse Gemini response
        idv_result = self._parse_gemini_response(gemini_response)
        
        # Step 6: Backend validation (20% rule) and age correction
        validated_result = self._validate_idv(idv_result, rc_data)
        
        # Add model name to result
        validated_result['ai_model'] = self.model_name
        
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
    
    def _create_gemini_prompt(self, data):
        """Create structured prompt for Gemini with 6-layer valuation logic"""
        
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
GOOGLE SEARCH INTEGRATION
================================

You have REAL-TIME Google Search access. Use it to:

1. SEARCH CURRENT PRICES:
   - "site:cardekho.com {data['maker_model']} {data['manufacturing_date'][:4]} price"
   - "site:olx.in {data['maker_model']} {data['city']} used car"
   - "site:droom.in {data['maker_model']} price {data['manufacturing_date'][:4]}"
   - "site:spinny.com {data['maker_model']} used"

2. VERIFY SPECIFICATIONS:
   - "{data['maker_model']} ex-showroom price {data['manufacturing_date'][:4]} India"
   - "{data['maker_model']} on-road price {data['city']} {data['manufacturing_date'][:4]}"

3. MARKET RESEARCH:
   - "{data['maker_model']} discontinued India"
   - "{data['maker_model']} new generation launch"
   - "{data['maker_model']} resale value {data['city']}"

4. REAL-TIME DATA:
   - Search for ACTUAL listings, not estimates
   - Get median of 3-5 real listings
   - Verify prices are from last 30 days
   - Cross-check multiple sources

================================
AI LEARNING & REASONING
================================

You have access to real-time web search and Indian automotive market knowledge.
Use your intelligence to:

1. PRICE DISCOVERY:
   - Search multiple sources (CarDekho, OLX, Droom, BikeWale, Spinny)
   - Cross-validate prices across platforms
   - Identify outliers and filter unrealistic listings
   - Consider seasonal trends (festive discounts, year-end sales)

2. MARKET ANALYSIS:
   - Analyze demand-supply dynamics for this model
   - Check if model is popular/rare in the region
   - Identify if it's a fleet vehicle (taxi/commercial)
   - Detect accident history indicators from listing descriptions

3. INTELLIGENT ADJUSTMENTS:
   - Learn from listing patterns (quick sales = underpriced)
   - Adjust for current fuel prices impact on diesel/petrol demand
   - Factor in upcoming BS7 norms impact on older vehicles
   - Consider insurance claim history if available

4. REASONING:
   - If prices vary widely, explain why in confidence score
   - If model is rare, reduce confidence but don't fail
   - If conflicting data, prioritize official sources
   - Use common sense: ₹50L for 2010 Alto = error

5. ADAPTIVE LEARNING:
   - Remember: Premium brands depreciate slower
   - EVs: Battery warranty remaining affects value significantly
   - Diesel: Post-2015 vehicles have better resale in non-NCR
   - Automatic transmission: +8-12% premium in metros

6. MACHINE LEARNING PATTERNS:
   - Pattern Recognition: Identify similar vehicles sold recently
   - Time Series Analysis: Track price trends over last 6 months
   - Anomaly Detection: Flag unusual price points (too high/low)
   - Clustering: Group similar vehicles by age, mileage, condition
   - Regression: Predict fair value based on historical transactions

7. NEURAL NETWORK THINKING:
   - Multi-factor correlation: How age + mileage + owner count interact
   - Non-linear relationships: Luxury cars don't follow linear depreciation
   - Feature importance: Which factors matter most for THIS specific model
   - Ensemble approach: Combine multiple valuation methods, weight by confidence

8. DEEP LEARNING INSIGHTS:
   - Natural Language Processing: Analyze listing descriptions for condition clues
   - Image recognition (if available): Assess vehicle condition from photos
   - Sentiment analysis: Gauge market sentiment for this brand/model
   - Transfer learning: Apply knowledge from similar models

9. REINFORCEMENT LEARNING:
   - Learn from feedback: If valuation differs from actual sale, adjust
   - Reward accuracy: Prioritize methods that historically worked
   - Explore-exploit: Try new approaches while using proven ones
   - Policy optimization: Refine valuation strategy over time

10. PREDICTIVE ANALYTICS:
    - Forecast future value: Will this model appreciate/depreciate faster?
    - Market timing: Is now good time to buy/sell this model?
    - Risk assessment: Probability of major repairs in next 2 years
    - Demand prediction: Will demand increase (new gen launch, fuel crisis)?

11. DUAL-ENGINE VALUATION SYSTEM:
    - ICE Engine: Use depreciation grid, mileage adjustments, regional penalties
    - EV Engine: Use battery SoH, chemistry type, warranty cliff, replacement cost
    - Auto-detect fuel type and route to correct engine
    - Apply owner count penalty: +4% per additional owner
    - NCR diesel ban logic: Scrap value if >9.5 years
    - South India premium: +8% for KA/TS/TN/KL/AP
    - Market convergence: Blend book value with market listings
    - Dealer economics: Calculate purchase offer with margins and refurb costs

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
        """Call Gemini API with proper error handling"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
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
            print(f"DEBUG: Response object: {response}")
            raise ValueError("Empty response from Gemini")
                
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
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
