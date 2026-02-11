import requests
import json
from datetime import datetime

class RCAPIClient:
    """
    Surepass RC API Client for fetching vehicle details
    """
    
    def __init__(self, api_token):
        self.base_url = "https://kyc-api.surepass.app/api/v1/rc/rc-v2"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'
        }
    
    def fetch_vehicle_details(self, rc_number):
        """
        Fetch vehicle details from RC API
        
        Args:
            rc_number (str): Vehicle registration number (e.g., "DL08AB1234")
        
        Returns:
            dict: Parsed vehicle data or None if failed
        """
        payload = {
            "id_number": rc_number,
            "enrich": True
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return self._parse_rc_response(result['data'])
                else:
                    print(f"API Error: {result.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"HTTP Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None
    
    def _parse_rc_response(self, data):
        """
        Parse RC API response into valuation engine format
        """
        # Extract make and model from maker_description and maker_model
        maker_desc = data.get('maker_description', '')
        maker_model = data.get('maker_model', '')
        
        # Parse make (manufacturer)
        make = self._extract_make(maker_desc)
        
        # Parse body type
        body_type = self._map_body_type(data.get('body_type', ''))
        
        # Parse registration date
        reg_date = data.get('registration_date', '')
        
        # Extract RTO code from RC number
        rc_number = data.get('rc_number', '')
        rto_code = self._extract_rto_code(rc_number)
        
        # Extract city from registered_at
        registered_at = data.get('registered_at', '')
        city = self._extract_city(registered_at)
        
        # Parse color
        color = data.get('color', '').title()
        
        # Parse fuel type
        fuel_type = data.get('fuel_type', '').title()
        
        # Owner count
        owner_count = int(data.get('owner_number', 1))
        
        return {
            'rc_number': rc_number,
            'make': make,
            'model': maker_model,
            'variant': '',  # Not provided by API
            'fuel_type': fuel_type,
            'reg_date': reg_date,
            'rto_code': rto_code,
            'city': city,
            'body_type': body_type,
            'color': color,
            'owner_count': owner_count,
            'manufacturing_date': data.get('manufacturing_date_formatted', ''),
            'insurance_upto': data.get('insurance_upto', ''),
            'tax_upto': data.get('tax_upto', ''),
            'financed': data.get('financed', False),
            'blacklist_status': data.get('blacklist_status', ''),
            'raw_data': data
        }
    
    def _extract_make(self, maker_description):
        """Extract manufacturer name from maker description"""
        make_mapping = {
            'HONDA': 'Honda',
            'MARUTI': 'Maruti Suzuki',
            'SUZUKI': 'Maruti Suzuki',
            'HYUNDAI': 'Hyundai',
            'TATA': 'Tata',
            'MAHINDRA': 'Mahindra',
            'TOYOTA': 'Toyota',
            'KIA': 'Kia',
            'FORD': 'Ford',
            'VOLKSWAGEN': 'Volkswagen',
            'SKODA': 'Skoda',
            'RENAULT': 'Renault',
            'NISSAN': 'Nissan',
            'MERCEDES': 'Mercedes-Benz',
            'BMW': 'BMW',
            'AUDI': 'Audi'
        }
        
        maker_upper = maker_description.upper()
        for key, value in make_mapping.items():
            if key in maker_upper:
                return value
        
        # Default: return first word
        return maker_description.split()[0] if maker_description else 'Unknown'
    
    def _map_body_type(self, api_body_type):
        """Map API body type to valuation engine categories"""
        body_type_mapping = {
            'SCOOTER': 'Hatchback',  # Treat 2-wheelers as Hatchback for margin calculation
            'MOTORCYCLE': 'Hatchback',
            'HATCHBACK': 'Hatchback',
            'SEDAN': 'Sedan',
            'SUV': 'SUV',
            'MUV': 'SUV',
            'LUXURY': 'Luxury',
            'COUPE': 'Luxury',
            'CONVERTIBLE': 'Luxury'
        }
        
        return body_type_mapping.get(api_body_type.upper(), 'Hatchback')
    
    def _extract_rto_code(self, rc_number):
        """Extract RTO code from RC number (e.g., DL08AB1234 -> DL08)"""
        if len(rc_number) >= 4:
            return rc_number[:4]
        return rc_number
    
    def _extract_city(self, registered_at):
        """Extract city from registered_at field"""
        if ',' in registered_at:
            return registered_at.split(',')[0].strip()
        return registered_at.strip()


def get_vehicle_valuation_from_rc(rc_number, api_token, current_ex_showroom, market_listings_mean=None):
    """
    Complete workflow: Fetch RC details and calculate valuation
    
    Args:
        rc_number (str): Vehicle registration number
        api_token (str): Surepass API token
        current_ex_showroom (float): Current ex-showroom price of equivalent new model
        market_listings_mean (float, optional): Average market listing price
    
    Returns:
        dict: Complete valuation result with RC details
    """
    from vehicle_valuation import calculate_resale_value
    
    # Fetch RC details
    client = RCAPIClient(api_token)
    rc_data = client.fetch_vehicle_details(rc_number)
    
    if not rc_data:
        return {
            'success': False,
            'error': 'Failed to fetch RC details'
        }
    
    # Prepare valuation input
    valuation_input = {
        'make': rc_data['make'],
        'model': rc_data['model'],
        'variant': rc_data['variant'],
        'fuel_type': rc_data['fuel_type'],
        'reg_date': rc_data['reg_date'],
        'rto_code': rc_data['rto_code'],
        'city': rc_data['city'],
        'body_type': rc_data['body_type'],
        'color': rc_data['color'],
        'owner_count': rc_data['owner_count'],
        'current_ex_showroom': current_ex_showroom
    }
    
    if market_listings_mean:
        valuation_input['market_listings_mean'] = market_listings_mean
    
    # Calculate valuation
    valuation_result = calculate_resale_value(valuation_input)
    
    # Combine results
    return {
        'success': True,
        'rc_details': rc_data,
        'valuation': valuation_result
    }


# Example usage
if __name__ == '__main__':
    # Replace with your actual API token
    API_TOKEN = "your_surepass_api_token_here"
    
    # Example: Fetch and value a vehicle
    result = get_vehicle_valuation_from_rc(
        rc_number="DL08AB1234",
        api_token=API_TOKEN,
        current_ex_showroom=75000,  # Honda Activa current price
        market_listings_mean=45000
    )
    
    if result['success']:
        print("RC Details:")
        print(json.dumps(result['rc_details'], indent=2))
        print("\nValuation:")
        print(json.dumps(result['valuation'], indent=2))
    else:
        print(f"Error: {result['error']}")
