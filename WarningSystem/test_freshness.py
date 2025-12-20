"""
Test script to examine the location response structure and timestamp fields
"""
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import json

load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")
headers = {"X-API-Key": API_KEY} if API_KEY else {}

# Search for locations near Delhi
params = {
    "coordinates": "28.6139,77.2090",
    "radius": 10000,
    "limit": 10
}

print("=== Fetching 10 locations near Delhi ===")
r = requests.get("https://api.openaq.org/v3/locations", params=params, headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"\nFound {len(data.get('results', []))} locations\n")
    
    for i, location in enumerate(data.get('results', [])[:5], 1):
        print(f"\n--- Location {i} ---")
        print(f"ID: {location.get('id')}")
        print(f"Name: {location.get('name')}")
        print(f"Coordinates: {location.get('coordinates')}")
        
        # Check for timestamp fields
        print(f"\nTimestamp fields:")
        for key in location.keys():
            if 'time' in key.lower() or 'date' in key.lower() or 'last' in key.lower() or 'update' in key.lower():
                print(f"  {key}: {location[key]}")
        
        # Pretty print the entire location object for the first one
        if i == 1:
            print(f"\nFull structure of first location:")
            print(json.dumps(location, indent=2))
else:
    print(f"Error: {r.text}")
