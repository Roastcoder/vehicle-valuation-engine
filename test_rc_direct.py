import os
import json
from dotenv import load_dotenv
from rc_api_integration import RCAPIClient

load_dotenv()

RC_NUMBER = "rj27cm8183"
API_TOKEN = os.getenv('SUREPASS_API_TOKEN')

if not API_TOKEN:
    print("Error: SUREPASS_API_TOKEN not found in .env file")
    exit(1)

print(f"Fetching RC details for: {RC_NUMBER}")
print("=" * 60)

client = RCAPIClient(API_TOKEN)
result = client.fetch_vehicle_details(RC_NUMBER)

if result:
    print("\n✅ SUCCESS - RC Details Retrieved\n")
    print(json.dumps(result, indent=2))
else:
    print("\n❌ FAILED - Could not fetch RC details")
