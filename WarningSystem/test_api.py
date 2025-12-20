"""
Test script to diagnose OpenAQ API v3 geospatial search
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")

print(f"API Key loaded: {'Yes' if API_KEY else 'No'}")
print(f"API Key (first 10 chars): {API_KEY[:10] if API_KEY else 'N/A'}")

# Test 1: Basic coordinates + radius (no sorting)
print("\n=== TEST 1: Basic coordinates + radius ===")
params1 = {
    "coordinates": "28.6139,77.2090",
    "radius": 25000,
    "limit": 1
}
headers = {"X-API-Key": API_KEY} if API_KEY else {}
r1 = requests.get("https://api.openaq.org/v3/locations", params=params1, headers=headers)
print(f"Status: {r1.status_code}")
print(f"URL: {r1.url}")
print(f"Response: {r1.text[:300]}")

# Test 2: With order_by and sort
print("\n=== TEST 2: With order_by and sort ===")
params2 = {
    "coordinates": "28.6139,77.2090",
    "radius": 25000,
    "limit": 1,
    "order_by": "lastUpdated",
    "sort": "desc"
}
r2 = requests.get("https://api.openaq.org/v3/locations", params=params2, headers=headers)
print(f"Status: {r2.status_code}")
print(f"URL: {r2.url}")
print(f"Response: {r2.text[:300]}")

# Test 3: Try different order_by values
print("\n=== TEST 3: Different order_by ===")
params3 = {
    "coordinates": "28.6139,77.2090",
    "radius": 25000,
    "limit": 1,
    "sort_by": "lastUpdated",
    "sort_order": "desc"
}
r3 = requests.get("https://api.openaq.org/v3/locations", params=params3, headers=headers)
print(f"Status: {r3.status_code}")
print(f"URL: {r3.url}")
print(f"Response: {r3.text[:300]}")
