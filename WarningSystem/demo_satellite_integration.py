"""
Demonstration of complete satellite integration
Shows how satellite data flows through the system
"""

from src.satellite import fetch_sentinel_indices
from src.ai_engine import generate_comprehensive_advisory
from src import config
import json

print("=" * 70)
print("  SATELLITE DATA INTEGRATION DEMONSTRATION")
print("=" * 70)

# Step 1: Fetch Satellite Data
print("\n[STEP 1] Fetching Satellite Data for Delhi...")
sat_data = fetch_sentinel_indices(
    config.LOCATION_COORDS["latitude"],
    config.LOCATION_COORDS["longitude"]
)

print(f"[SATELLITE] {sat_data['satellite']} Data Loaded")
print(f"|-- Water ({sat_data['water']['index']}): {sat_data['water']['value']:.3f} ({sat_data['water']['status']})")
print(f"|-- Land ({sat_data['land']['index']}): {sat_data['land']['value']:.3f} ({sat_data['land']['status']})")
print(f"|-- Last Pass: {sat_data['last_pass']}")

# Step 2: Simulate Air Quality Data
print("\n[STEP 2] Simulating Air Quality Analysis...")
sensor_data = {
    "current_value": 125.8,  # Unhealthy level
    "status": "DISTRESS",
    "z_score": 2.3,
    "baseline_mean": 68.5,
    "baseline_std": 15.2
}
print(f"PM2.5: {sensor_data['current_value']} µg/m³ (Status: {sensor_data['status']})")

# Step 3: Generate AI Advisory with Satellite Data
print("\n[STEP 3] Generating AI Advisory with Environmental Context...")
print("=" * 70)
advisory = generate_comprehensive_advisory(sensor_data, satellite_data=sat_data)
print(advisory)
print("=" * 70)

# Step 4: Show JSON Export Structure
print("\n[STEP 4] JSON Export Structure:")
export_data = {
    "timestamp": "2025-12-20T18:49:00+05:30",
    "status": sensor_data["status"],
    "current_value": sensor_data["current_value"],
    "satellite_data": sat_data,
    "ai_message": "[AI Advisory shown above]"
}
print(json.dumps(export_data, indent=2))

print("\n" + "=" * 70)
print("  DEMONSTRATION COMPLETE")
print("  ✅ Satellite data successfully integrated")
print("  ✅ AI synthesizes Air, Water, and Land metrics")
print("  ✅ Complete environmental intelligence system")
print("=" * 70)
