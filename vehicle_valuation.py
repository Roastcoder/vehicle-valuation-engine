from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

def calculate_resale_value(vehicle_data):
    """
    Used Vehicle Resale Value Predictor for Indian Market
    Returns Fair Market Retail Value and Dealer Purchase Price
    """
    
    # Parse input
    make = vehicle_data['make']
    model = vehicle_data['model']
    variant = vehicle_data.get('variant', '')
    fuel_type = vehicle_data['fuel_type']
    reg_date = datetime.strptime(vehicle_data['reg_date'], '%Y-%m-%d')
    rto_code = vehicle_data['rto_code']
    city = vehicle_data['city']
    body_type = vehicle_data['body_type']
    color = vehicle_data['color']
    owner_count = vehicle_data.get('owner_count', 1)
    current_ex_showroom = vehicle_data['current_ex_showroom']
    market_listings_mean = vehicle_data.get('market_listings_mean')
    odometer = vehicle_data.get('odometer')
    
    # ===== LAYER 1: DERIVED METRICS =====
    current_date = datetime.now()
    age_delta = relativedelta(current_date, reg_date)
    age_years = age_delta.years + age_delta.months / 12
    age_months = age_delta.years * 12 + age_delta.months
    
    # Standard odometer if not provided
    if odometer is None:
        odometer = age_months * 1000
    
    # Mileage deviation
    mileage_adjustment = 0
    if age_years > 0:
        avg_annual_running = odometer / age_years
        if avg_annual_running > 15000:
            mileage_adjustment = 0.05  # High usage penalty
        elif avg_annual_running < 6000:
            mileage_adjustment = -0.03  # Low usage bonus
    
    # ===== LAYER 2: BASE DEPRECIATION =====
    if age_years < 0.5:
        base_depreciation = 0.05
    elif age_years < 1:
        base_depreciation = 0.10
    elif age_years < 2:
        base_depreciation = 0.18
    elif age_years < 3:
        base_depreciation = 0.25
    elif age_years < 4:
        base_depreciation = 0.30
    elif age_years < 5:
        base_depreciation = 0.35
    elif age_years < 6:
        base_depreciation = 0.40
    elif age_years < 7:
        base_depreciation = 0.45
    elif age_years < 8:
        base_depreciation = 0.50
    else:
        base_depreciation = 0.60
    
    # Apply mileage adjustment
    base_depreciation += mileage_adjustment
    base_depreciation = min(base_depreciation, 0.75)  # Cap at 75%
    
    # Historical price estimation (reverse inflation)
    estimated_historical = current_ex_showroom * (1 - (0.03 * age_years))
    
    # Book value calculation
    book_value = estimated_historical * (1 - base_depreciation)
    
    # ===== LAYER 3: MARKET INTELLIGENCE =====
    market_penalty = 0
    
    # Discontinued models database
    discontinued_models = [
        'Ecosport', 'Figo', 'Aspire', 'Civic', 'CR-V', 'Yaris', 
        'Etios', 'Corolla Altis', 'Punto', 'Linea', 'Aveo', 'Beat', 'Sail'
    ]
    if any(disc in model for disc in discontinued_models):
        market_penalty += 0.15
    
    # New generation launch
    new_gen_models = [
        'Swift', 'Dzire', 'Baleno', 'Creta', 'Venue', 'i20', 'Verna',
        'Seltos', 'Sonet', 'City', 'Amaze', 'WR-V', 'Brezza', 'Ertiga'
    ]
    if any(ng in model for ng in new_gen_models) and age_years > 3:
        market_penalty += 0.10
    
    # Color factor
    preferred_colors = ['White', 'Silver', 'Grey', 'Black']
    if color not in preferred_colors:
        market_penalty += 0.02
    
    book_value *= (1 - market_penalty)
    
    # ===== LAYER 4: REGIONAL LOGIC =====
    regional_adjustment = 1.0
    
    # NCR Diesel Ban
    ncr_cities = ['Delhi', 'Noida', 'Gurgaon', 'Gurugram', 'Faridabad', 'Ghaziabad']
    if any(ncr in city for ncr in ncr_cities) and fuel_type == 'Diesel':
        if age_years > 9.5:
            # Scrap value only (assume 2% of original)
            book_value = estimated_historical * 0.02
            regional_adjustment = 1.0
        elif age_years > 8:
            regional_adjustment = 0.75  # 25% penalty
    
    # South India Premium
    south_rto_prefixes = ['KA', 'TS', 'TN', 'KL', 'AP']
    if any(rto_code.startswith(prefix) for prefix in south_rto_prefixes):
        regional_adjustment *= 1.12
    
    # Coastal Corrosion
    coastal_cities = ['Mumbai', 'Chennai', 'Kolkata', 'Goa', 'Visakhapatnam']
    if any(coastal in city for coastal in coastal_cities) and age_years > 5:
        regional_adjustment *= 0.96
    
    book_value *= regional_adjustment
    
    # ===== LAYER 5: VALUATION CONVERGENCE =====
    if market_listings_mean:
        if age_years < 5:
            fair_market_value = (0.70 * market_listings_mean) + (0.30 * book_value)
        else:
            fair_market_value = (0.50 * market_listings_mean) + (0.50 * book_value)
    else:
        fair_market_value = book_value
    
    # Negotiation gap (7% reduction)
    fair_market_retail_value = fair_market_value * 0.93
    
    # ===== LAYER 6: DEALER ECONOMICS =====
    # Dealer margin
    if body_type == 'Luxury':
        dealer_margin = 0.15
        refurb_cost = 25000
    elif body_type in ['Sedan', 'SUV']:
        dealer_margin = 0.12
        refurb_cost = 15000
    else:  # Hatchback
        dealer_margin = 0.10
        refurb_cost = 8000
    
    dealer_purchase_price = fair_market_retail_value * (1 - dealer_margin) - refurb_cost
    
    # Ensure non-negative values
    dealer_purchase_price = max(dealer_purchase_price, 0)
    
    # Return results
    return {
        'fair_market_retail_value': round(fair_market_retail_value, 2),
        'dealer_purchase_price': round(dealer_purchase_price, 2),
        'metadata': {
            'vehicle_age_years': round(age_years, 2),
            'estimated_odometer': odometer,
            'base_depreciation_percent': round(base_depreciation * 100, 2),
            'book_value': round(book_value, 2),
            'regional_adjustment_factor': round(regional_adjustment, 2)
        }
    }


# Example usage
if __name__ == '__main__':
    sample_vehicle = {
        'make': 'Maruti Suzuki',
        'model': 'Swift',
        'variant': 'VXI',
        'fuel_type': 'Petrol',
        'reg_date': '2019-03-15',
        'rto_code': 'DL3C',
        'city': 'Delhi',
        'body_type': 'Hatchback',
        'color': 'White',
        'owner_count': 1,
        'current_ex_showroom': 650000,
        'market_listings_mean': 425000,
        'odometer': 45000
    }
    
    result = calculate_resale_value(sample_vehicle)
    print(json.dumps(result, indent=2))
