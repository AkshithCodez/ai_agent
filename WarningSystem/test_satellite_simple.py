"""
Simple test for satellite data only
"""
from src.satellite import fetch_sentinel_air_quality
import json

print("Testing Sentinel-5P Air Quality Module...")
print("=" * 50)

for i in range(3):
    print(f"\nTest Run {i+1}:")
    data = fetch_sentinel_air_quality(17.3850, 78.4867)
    print(f"  🚗 NO2: {data['no2']['value']:.3f} ({data['no2']['status']})")
    print(f"  💨 Aerosol Index: {data['aerosol']['value']:.2f} ({data['aerosol']['status']})")
    print(f"  Last Pass: {data['last_pass']}")

print("\n" + "=" * 50)
print("Full JSON structure (last run):")
print(json.dumps(data, indent=2))
