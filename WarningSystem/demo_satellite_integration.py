"""
Demonstration of complete Sentinel-5P satellite integration
Shows how air quality data (NO2, Aerosol Index) flows through the system
"""

from src.satellite import fetch_sentinel_air_quality
from src.ai_engine import generate_comprehensive_advisory
from src import config
import json

print("=" * 70)
print("  SENTINEL-5P AIR QUALITY INTEGRATION DEMONSTRATION")
print("=" * 70)

# Step 1: Fetch Sentinel-5P Air Quality Data
print("\n[STEP 1] Fetching Sentinel-5P Air Quality Data for Hyderabad...")
sat_data = fetch_sentinel_air_quality(
    config.LOCATION_COORDS["latitude"],
    config.LOCATION_COORDS["longitude"]
)

print(f"[SATELLITE] {sat_data['satellite']} Data Loaded")
print(f"|-- 🚗 NO2 ({sat_data['no2']['index']}): {sat_data['no2']['value']:.3f} ({sat_data['no2']['status']})")
print(f"|-- 💨 Aerosol ({sat_data['aerosol']['index']}): {sat_data['aerosol']['value']:.2f} ({sat_data['aerosol']['status']})")
print(f"|-- Last Pass: {sat_data['last_pass']}")

# Step 2: Simulate Air Quality Data
print("\n[STEP 2] Simulating Air Quality Analysis...")
sensor_data = {
    "current_value": 125.8,
    "status": "DISTRESS",
    "z_score": 2.3,
    "baseline_mean": 68.5,
    "baseline_std": 15.2
}
print(f"PM2.5: {sensor_data['current_value']} µg/m³ (Status: {sensor_data['status']})")

# Step 3: Generate AI Advisory with Air Quality Satellite Data
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
print("  ✅ Sentinel-5P air quality data successfully integrated")
print("  ✅ AI synthesizes PM2.5 with NO2/Aerosol metrics")
print("  ✅ Air pollution intelligence system operational")
print("=" * 70)
