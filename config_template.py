# Configuration Template
# Copy this file to config.py and add your actual credentials

# Surepass RC API Configuration
SUREPASS_API_TOKEN = "your_surepass_api_token_here"
SUREPASS_API_URL = "https://kyc-api.surepass.app/api/v1/rc/rc-v2"

# Google Gemini API Configuration
GEMINI_API_KEY = "your_gemini_api_key_here"
# Get your key from: https://makersuite.google.com/app/apikey

# Optional: Market Data API (if you have one)
MARKET_DATA_API_TOKEN = ""
MARKET_DATA_API_URL = ""

# Default Values
DEFAULT_MARKET_LISTING_WEIGHT = 0.7  # For cars < 5 years
DEFAULT_NEGOTIATION_GAP = 0.07  # 7% reduction

# Dealer Margins
DEALER_MARGINS = {
    'Hatchback': {'margin': 0.10, 'refurb_cost': 8000},
    'Sedan': {'margin': 0.12, 'refurb_cost': 15000},
    'SUV': {'margin': 0.12, 'refurb_cost': 15000},
    'Luxury': {'margin': 0.15, 'refurb_cost': 25000}
}

# Regional Adjustments
REGIONAL_ADJUSTMENTS = {
    'south_india_premium': 1.12,
    'coastal_corrosion_penalty': 0.96,
    'ncr_diesel_ban_penalty': 0.75
}

# IDV Validation
IDV_VALIDATION_THRESHOLD = 20  # 20% difference threshold
