"""
Test script to find the correct measurements endpoint for OpenAQ v3
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")
headers = {"X-API-Key": API_KEY} if API_KEY else {}

location_id = 13  # Delhi Technological University

# Test 1: /v3/locations/{id}/latest (for latest measurements)
print("=== TEST 1: /v3/locations/{id}/latest ===")
url1 = f"https://api.openaq.org/v3/locations/{location_id}/latest"
r1 = requests.get(url1, headers=headers)
print(f"Status: {r1.status_code}")
print(f"URL: {r1.url}")
if r1.status_code == 200:
    data = r1.json()
    print(f"Response keys: {data.keys()}")
    if 'results' in data:
        print(f"Number of results: {len(data['results'])}")
        if len(data['results']) > 0:
            print(f"First result keys: {data['results'][0].keys()}")
            print(f"Sample data: {data['results'][0]}")
else:
    print(f"Error: {r1.text[:200]}")

# Test 2: Global /v3/measurements with locations_id
print("\n=== TEST 2: /v3/measurements with locations_id ===")
url2 = "https://api.openaq.org/v3/measurements"
params2 = {"locations_id": location_id, "limit": 5}
r2 = requests.get(url2, params=params2, headers=headers)
print(f"Status: {r2.status_code}")
print(f"URL: {r2.url}")
if r2.status_code == 200:
    data = r2.json()
    print(f"Response keys: {data.keys()}")
    if 'results' in data:
        print(f"Number of results: {len(data['results'])}")
else:
    print(f"Error: {r2.text[:200]}")

# Test 3: Try with location (singular) instead of locations
print("\n=== TEST 3: /v3/measurements with location_id ===")
params3 = {"location_id": location_id, "limit": 5}
r3 = requests.get(url2, params=params3, headers=headers)
print(f"Status: {r3.status_code}")
print(f"URL: {r3.url}")
if r3.status_code == 200:
    data = r3.json()
    print(f"Response keys: {data.keys()}")
else:
    print(f"Error: {r3.text[:200]}")
