"""
Insurance-Grade Vehicle Valuation Engine
Deterministic, consistent, and never reuses full valuations across different RCs
"""

from datetime import datetime
import json


class InsuranceGradeValuationEngine:
    """
    Strict valuation engine that ensures:
    - No full valuation reuse across different RCs
    - Market data reuse only for matching specs
    - Variant-specific calculations
    - Month-level depreciation accuracy
    - Owner count impact
    - Deterministic outputs
    """
    
    MONTHLY_DEPRECIATION_RATE = 0.008  # 0.8% per month
    OWNER_2_PENALTY = 0.97  # 3% reduction for 2nd owner
    OWNER_3_PLUS_PENALTY = 0.94  # 6% reduction for 3+ owners
    MARKET_CACHE_MAX_AGE_DAYS = 45
    
    def calculate_idv(self, input_data):
        """
        Calculate Insurance Declared Value with strict rules
        
        Args:
            input_data: Dict with registration_number, make, base_model, variant,
                       fuel, transmission, manufacturing_year, manufacturing_month,
                       city, owner_count, base_ex_showroom, variant_ex_showroom,
                       market_listings_mean, market_cache_age_days
        
        Returns:
            Dict with final_idv, adjusted_market_value, months_old,
                 owner_adjustment_applied, confidence_score, reasoning_summary
        """
        
        # Step 1: Validate market cache age
        market_cache_age = input_data.get('market_cache_age_days', 0)
        if market_cache_age > self.MARKET_CACHE_MAX_AGE_DAYS:
            return {
                'status': 'MARKET_REFRESH_REQUIRED',
                'reason': f'Market cache is {market_cache_age} days old (max: {self.MARKET_CACHE_MAX_AGE_DAYS})',
                'registration_number': input_data.get('registration_number'),
                'cache_specs': {
                    'make': input_data.get('make'),
                    'base_model': input_data.get('base_model'),
                    'fuel': input_data.get('fuel'),
                    'transmission': input_data.get('transmission'),
                    'manufacturing_year': input_data.get('manufacturing_year'),
                    'city': input_data.get('city')
                }
            }
        
        # Step 2: Variant Adjustment
        base_ex_showroom = float(input_data.get('base_ex_showroom', 0))
        variant_ex_showroom = float(input_data.get('variant_ex_showroom', 0))
        market_listings_mean = float(input_data.get('market_listings_mean', 0))
        
        if base_ex_showroom == 0 or variant_ex_showroom == 0:
            return {
                'status': 'ERROR',
                'reason': 'Missing ex-showroom prices',
                'registration_number': input_data.get('registration_number')
            }
        
        variant_ratio = variant_ex_showroom / base_ex_showroom
        adjusted_market_value = market_listings_mean * variant_ratio
        
        # Step 3: Month-Level Depreciation
        manufacturing_year = int(input_data.get('manufacturing_year'))
        manufacturing_month = int(input_data.get('manufacturing_month'))
        
        current_date = datetime.now()
        manufacturing_date = datetime(manufacturing_year, manufacturing_month, 1)
        
        months_old = (current_date.year - manufacturing_date.year) * 12 + \
                     (current_date.month - manufacturing_date.month)
        
        depreciated_value = adjusted_market_value * (1 - self.MONTHLY_DEPRECIATION_RATE * months_old)
        
        # Step 4: Owner Adjustment
        owner_count = int(input_data.get('owner_count', 1))
        owner_adjustment_applied = 1.0
        
        if owner_count == 2:
            depreciated_value *= self.OWNER_2_PENALTY
            owner_adjustment_applied = self.OWNER_2_PENALTY
        elif owner_count >= 3:
            depreciated_value *= self.OWNER_3_PLUS_PENALTY
            owner_adjustment_applied = self.OWNER_3_PLUS_PENALTY
        
        # Step 5: Final IDV (rounded to nearest 1000)
        final_idv = round(depreciated_value / 1000) * 1000
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            market_cache_age,
            variant_ratio,
            months_old,
            market_listings_mean
        )
        
        # Generate reasoning summary
        reasoning_summary = self._generate_reasoning(
            input_data,
            variant_ratio,
            months_old,
            owner_count,
            owner_adjustment_applied,
            adjusted_market_value,
            depreciated_value,
            final_idv
        )
        
        return {
            'status': 'SUCCESS',
            'registration_number': input_data.get('registration_number'),
            'final_idv': final_idv,
            'adjusted_market_value': round(adjusted_market_value, 2),
            'months_old': months_old,
            'owner_adjustment_applied': owner_adjustment_applied,
            'confidence_score': round(confidence_score, 2),
            'reasoning_summary': reasoning_summary,
            'calculation_breakdown': {
                'base_ex_showroom': base_ex_showroom,
                'variant_ex_showroom': variant_ex_showroom,
                'variant_ratio': round(variant_ratio, 4),
                'market_listings_mean': market_listings_mean,
                'adjusted_market_value': round(adjusted_market_value, 2),
                'monthly_depreciation_rate': self.MONTHLY_DEPRECIATION_RATE,
                'total_depreciation_percent': round(self.MONTHLY_DEPRECIATION_RATE * months_old * 100, 2),
                'value_after_depreciation': round(depreciated_value, 2),
                'owner_penalty': round((1 - owner_adjustment_applied) * 100, 2),
                'final_idv': final_idv
            }
        }
    
    def _calculate_confidence(self, market_age, variant_ratio, months_old, market_mean):
        """Calculate confidence score (0-1)"""
        confidence = 1.0
        
        # Market freshness penalty
        if market_age > 30:
            confidence -= 0.1
        elif market_age > 15:
            confidence -= 0.05
        
        # Variant accuracy penalty
        if variant_ratio < 0.8 or variant_ratio > 1.3:
            confidence -= 0.15
        
        # Age precision bonus
        if months_old <= 12:
            confidence += 0.05
        
        # Market data quality
        if market_mean == 0:
            confidence -= 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_reasoning(self, input_data, variant_ratio, months_old, 
                           owner_count, owner_adj, adj_market, depreciated, final):
        """Generate human-readable reasoning"""
        
        reasoning = []
        
        # Vehicle identification
        reasoning.append(f"RC: {input_data.get('registration_number')}")
        reasoning.append(f"Vehicle: {input_data.get('make')} {input_data.get('base_model')} {input_data.get('variant')}")
        reasoning.append(f"Specs: {input_data.get('fuel')}, {input_data.get('transmission')}")
        
        # Variant adjustment
        reasoning.append(f"Variant ratio: {variant_ratio:.4f} (₹{input_data.get('variant_ex_showroom'):,.0f} / ₹{input_data.get('base_ex_showroom'):,.0f})")
        reasoning.append(f"Adjusted market value: ₹{adj_market:,.0f}")
        
        # Depreciation
        years = months_old // 12
        months = months_old % 12
        reasoning.append(f"Age: {years} years {months} months ({months_old} months total)")
        reasoning.append(f"Depreciation: {self.MONTHLY_DEPRECIATION_RATE * months_old * 100:.1f}% ({self.MONTHLY_DEPRECIATION_RATE * 100}% per month)")
        
        # Owner adjustment
        if owner_count == 1:
            reasoning.append(f"Owner: 1st owner (no penalty)")
        elif owner_count == 2:
            reasoning.append(f"Owner: 2nd owner ({(1-owner_adj)*100:.0f}% penalty)")
        else:
            reasoning.append(f"Owner: {owner_count}+ owners ({(1-owner_adj)*100:.0f}% penalty)")
        
        # Final
        reasoning.append(f"Final IDV: ₹{final:,.0f} (rounded to nearest ₹1,000)")
        
        return " | ".join(reasoning)


def validate_market_cache_key(vehicle_data):
    """
    Generate cache key for market data reuse
    Market data can ONLY be reused if ALL these match:
    - make
    - base_model
    - fuel
    - transmission
    - manufacturing_year
    - city
    """
    return {
        'make': vehicle_data.get('make', '').upper().strip(),
        'base_model': vehicle_data.get('base_model', '').upper().strip(),
        'fuel': vehicle_data.get('fuel', '').upper().strip(),
        'transmission': vehicle_data.get('transmission', '').upper().strip(),
        'manufacturing_year': str(vehicle_data.get('manufacturing_year', '')),
        'city': vehicle_data.get('city', '').upper().strip()
    }


def can_reuse_market_data(vehicle1, vehicle2):
    """
    Check if market data from vehicle1 can be reused for vehicle2
    Returns: (bool, reason)
    """
    key1 = validate_market_cache_key(vehicle1)
    key2 = validate_market_cache_key(vehicle2)
    
    mismatches = []
    for field in key1.keys():
        if key1[field] != key2[field]:
            mismatches.append(f"{field}: {key1[field]} != {key2[field]}")
    
    if mismatches:
        return False, f"Cannot reuse market data: {', '.join(mismatches)}"
    
    return True, "Market data can be reused (all specs match)"


# Example usage
if __name__ == '__main__':
    engine = InsuranceGradeValuationEngine()
    
    # Test case 1: Valid calculation
    test_input = {
        'registration_number': 'MH47BZ1005',
        'make': 'VOLKSWAGEN',
        'base_model': 'VIRTUS',
        'variant': 'GT LINE 1.0 TSI AT',
        'fuel': 'PETROL',
        'transmission': 'AUTOMATIC',
        'manufacturing_year': 2024,
        'manufacturing_month': 11,
        'city': 'MUMBAI',
        'owner_count': 1,
        'base_ex_showroom': 1100000,
        'variant_ex_showroom': 1650000,
        'market_listings_mean': 1326250,
        'market_cache_age_days': 5
    }
    
    result = engine.calculate_idv(test_input)
    print(json.dumps(result, indent=2))
    
    # Test case 2: Market refresh required
    test_input_old = test_input.copy()
    test_input_old['market_cache_age_days'] = 50
    test_input_old['registration_number'] = 'MH02GJ2882'
    
    result_old = engine.calculate_idv(test_input_old)
    print("\n" + json.dumps(result_old, indent=2))
