
"""
Quick test to verify satellite data integration with AI engine
"""

from src.satellite import fetch_sentinel_indices
from src.ai_engine import generate_comprehensive_advisory
import json

# Test 1: Fetch satellite data
print("=" * 70)
print("TEST 1: Satellite Data Generation")
print("=" * 70)
sat_data = fetch_sentinel_indices(28.6139, 77.2090)
print(json.dumps(sat_data, indent=2))

# Test 2: AI Advisory with satellite data
print("\n" + "=" * 70)
print("TEST 2: AI Advisory with Satellite Data")
print("=" * 70)

sensor_data = {
    "current_value": 85.5,
    "status": "WARNING",
    "z_score": 1.8,
    "baseline_mean": 65.2,
    "baseline_std": 12.3
}

advisory = generate_comprehensive_advisory(sensor_data, satellite_data=sat_data)
print(advisory)

# Test 3: AI Advisory without satellite data (fallback)
print("\n" + "=" * 70)
print("TEST 3: AI Advisory without Satellite Data")
print("=" * 70)

advisory_no_sat = generate_comprehensive_advisory(sensor_data, satellite_data=None)
print(advisory_no_sat)

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
