"""
Test the /latest endpoint for location 17 (R K Puram)
"""
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")
headers = {"X-API-Key": API_KEY} if API_KEY else {}

location_id = 17  # R K Puram

print(f"=== Testing /latest endpoint for location {location_id} ===")
url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
r = requests.get(url, headers=headers)

print(f"Status: {r.status_code}")
print(f"URL: {r.url}")

if r.status_code == 200:
    data = r.json()
    print(f"\nNumber of results: {len(data.get('results', []))}")
    
    # Show all results with their timestamps
    for i, result in enumerate(data.get('results', []), 1):
        print(f"\n--- Result {i} ---")
        print(f"Sensor ID: {result.get('sensorsId')}")
        print(f"Location ID: {result.get('locationsId')}")
        print(f"Value: {result.get('value')}")
        print(f"Datetime: {result.get('datetime')}")
        print(f"Coordinates: {result.get('coordinates')}")
    
    # Check for PM2.5 specifically
    print("\n=== Looking for PM2.5 data ===")
    for result in data.get('results', []):
        sensor_id = result.get('sensorsId')
        value = result.get('value')
        datetime_info = result.get('datetime', {})
        print(f"Sensor {sensor_id}: {value} at {datetime_info.get('utc')}")
else:
    print(f"Error: {r.text}")
