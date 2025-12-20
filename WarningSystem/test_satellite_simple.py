"""
Simple test for satellite data only
"""
from src.satellite import fetch_sentinel_indices
import json

print("Testing Satellite Module...")
print("=" * 50)

# Test multiple times to see variation
for i in range(3):
    print(f"\nTest Run {i+1}:")
    data = fetch_sentinel_indices(28.6139, 77.2090)
    print(f"  NDWI: {data['water']['value']:.3f} ({data['water']['status']})")
    print(f"  NDVI: {data['land']['value']:.3f} ({data['land']['status']})")
    print(f"  Last Pass: {data['last_pass']}")

print("\n" + "=" * 50)
print("Full JSON structure (last run):")
print(json.dumps(data, indent=2))
