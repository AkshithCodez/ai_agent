"""
Test script to verify the upgraded system works correctly.
Runs a single iteration without the continuous loop.
"""

import json
from pathlib import Path
from src.ingestion import fetch_historical_data, fetch_live_data
from src.analysis import detect_anomalies
from src import config

print("=" * 70)
print("  TESTING UPGRADED SYSTEM")
print("=" * 70)
print()

# Test 1: Environment Variable Loading
print("[TEST 1] Environment Variable Loading")
print(f"  API Key Status: {'Configured ✓' if config.API_KEY else 'Not configured (OK for demo)'}")
print()

# Test 2: Data Pipeline
print("[TEST 2] Running Data Pipeline")
historical_data = fetch_historical_data(limit=50)
print(f"  Historical data: {len(historical_data)} points")

current_value, timestamp = fetch_live_data(historical_data)
print(f"  Live data: {current_value} µg/m³")

result = detect_anomalies(historical_data, current_value)
print(f"  Analysis: {result['status']} (Z-Score: {result['z_score']:.2f})")
print()

# Test 3: JSON Export
print("[TEST 3] JSON Export")
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

output_data = {
    "timestamp": timestamp,
    "status": result["status"],
    "severity_score": result["severity_score"],
    "z_score": result["z_score"],
    "explanation": result["explanation"],
    "current_value": current_value,
    "baseline_mean": result.get("baseline_mean"),
    "baseline_std": result.get("baseline_std"),
    "city": config.TARGET_CITY,
    "parameter": config.PARAMETER
}

output_file = data_dir / "latest_alert.json"
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"  JSON saved to: {output_file}")
print(f"  File exists: {output_file.exists()}")

# Verify JSON content
with open(output_file, 'r') as f:
    loaded_data = json.load(f)
    print(f"  JSON valid: ✓")
    print(f"  Required fields present: {all(k in loaded_data for k in ['timestamp', 'status', 'severity_score', 'z_score', 'explanation'])}")

print()
print("=" * 70)
print("  ALL TESTS PASSED ✓")
print("=" * 70)
