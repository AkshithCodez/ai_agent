"""
Early Warning Intelligence Layer - Main Execution Script
Orchestrates the real-time air quality monitoring pipeline.
Runs continuously as a background service.
"""

from dotenv import load_dotenv
load_dotenv()

import json
import time
import os
import sys
from pathlib import Path
from src.ingestion import fetch_historical_data, fetch_live_data, discover_available_sensors, convert_to_ist
from src.analysis import detect_anomalies
from src.ai_adapter import get_ai_explanation
from src.satellite_manager import SentinelClient
from src import config
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def save_to_json(result: dict, current_value: float, timestamp: str):
    """
    Saves analysis results to JSON file for dashboard integration.
    
    Args:
        result: Analysis result dictionary from detect_anomalies
        current_value: Current measurement value
        timestamp: Timestamp of the measurement (in IST format)
    """
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
        "parameter": config.PARAMETER,
        "satellite_data": result.get("satellite_data", None),
        "ai_explanation": result.get("ai_explanation", "N/A"),
        "ai_message": result.get("ai_message", "N/A")
    }
    
    output_file = data_dir / "latest_alert.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"[EXPORT] Analysis saved to {output_file}")


def print_banner():
    """Prints the system startup banner."""
    print("=" * 70)
    print("  EARLY WARNING INTELLIGENCE LAYER")
    print("  Environmental Monitoring System v1.0")
    print("  Target: Hyderabad, India")
    print("=" * 70)
    print()


def print_diagnostic_report(result: dict, current_value: float, timestamp: str):
    """
    Prints a formatted diagnostic report.
    
    Args:
        result: Analysis result dictionary from detect_anomalies
        current_value: Current measurement value
        timestamp: Timestamp of the measurement (in IST format)
    """
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC REPORT")
    print("=" * 70)
    
    status_symbols = {
        "NORMAL": "✓",
        "WARNING": "⚠",
        "DISTRESS": "⚠⚠",
        "CRITICAL": "🚨",
        "ERROR": "✗"
    }
    
    symbol = status_symbols.get(result["status"], "?")
    
    print(f"\n{symbol} STATUS: {result['status']}")
    print(f"  Severity Score: {result['severity_score']}/3")
    print(f"\n📊 MEASUREMENTS:")
    print(f"  Current Value: {current_value:.2f} µg/m³")
    print(f"  Timestamp: {timestamp}")
    
    if result["baseline_mean"] is not None:
        print(f"\n📈 BASELINE STATISTICS:")
        print(f"  Mean: {result['baseline_mean']:.2f} µg/m³")
        print(f"  Std Dev: {result['baseline_std']:.2f} µg/m³")
    
    if result["z_score"] is not None:
        print(f"\n🔬 ANOMALY DETECTION:")
        print(f"  Z-Score: {result['z_score']:.2f}")
        print(f"  Thresholds:")
        print(f"    - Warning: ±{config.THRESHOLDS['LOW_WARNING']}")
        print(f"    - Distress: ±{config.THRESHOLDS['MEDIUM_DISTRESS']}")
        print(f"    - Critical: ±{config.THRESHOLDS['HIGH_CRITICAL']}")
    
    print(f"\n💡 EXPLANATION:")
    print(f"  {result['explanation']}")
    
    print("\n" + "=" * 70)


def select_sensor_interactively(location_coords: dict):
    """
    Displays available sensors and prompts user to select one.
    
    Args:
        location_coords: Dictionary with latitude and longitude
    
    Returns:
        Selected location ID (int), or None if no sensors available
    """
    print("\n" + "=" * 70)
    print("  SENSOR SELECTION")
    print("=" * 70 + "\n")
    
    sensors = discover_available_sensors(
        lat=location_coords.get("latitude"),
        lon=location_coords.get("longitude"),
        radius=10000
    )
    
    if not sensors or len(sensors) == 0:
        print("[WARNING] No fresh sensors found.")
        print("[INFO] The system will use simulated data.\n")
        return None
    
    print(f"Found {len(sensors)} fresh sensor(s):\n")
    for i, sensor in enumerate(sensors, 1):
        print(f"{i}. ID: {sensor['id']:5} | {sensor['name']:45} | Last Update: {sensor['last_updated_ist']}")
    
    while True:
        try:
            choice = input(f"\nSelect a sensor (1-{len(sensors)}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(sensors):
                selected = sensors[choice_num - 1]
                print(f"\n[SELECTED] {selected['name']} (ID: {selected['id']})")
                print(f"[INFO] Last updated: {selected['last_updated_ist']}\n")
                return selected['id']
            else:
                print(f"[ERROR] Please enter a number between 1 and {len(sensors)}")
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n[SYSTEM] Selection cancelled. Exiting...")
            return None


def run_pipeline(location_id=None, sentinel_client=None, location_coords=None):
    """
    Executes a single iteration of the monitoring pipeline.
    
    Args:
        location_id: Optional location ID to monitor. If None, auto-discovers.
        sentinel_client: SentinelClient instance for satellite data
        location_coords: Dictionary with latitude, longitude, and name
    
    Returns:
        True if successful, False otherwise.
    """
    print("[PIPELINE] Step 1/3: Establishing Baseline...")
    historical_data = fetch_historical_data(limit=config.HISTORICAL_LIMIT, location_id=location_id)
    
    if not historical_data:
        print("[WARNING] Failed to establish baseline. Skipping this iteration.")
        return False
    
    print(f"[SUCCESS] Baseline established with {len(historical_data)} data points.")
    print()
    
    print("[PIPELINE] Step 2/3: Fetching Live Data...")
    current_value, timestamp = fetch_live_data(historical_data, location_id=location_id)
    
    if current_value is None:
        print("[WARNING] Failed to fetch live data. Skipping this iteration.")
        return False
    
    print(f"[SUCCESS] Live data retrieved: {current_value} µg/m³")
    print()
    
    print("[PIPELINE] Step 2.5/4: Fetching Satellite Data from Sentinel Hub...")
    sat_data = None
    
    if sentinel_client and location_coords:
        try:
            lat = location_coords.get("latitude")
            lon = location_coords.get("longitude")
            
            sat_data = sentinel_client.get_air_quality_stats(lat, lon)
            
            if sat_data and sat_data.get("data_source") != "Unavailable":
                print(f"[SUCCESS] Satellite statistics retrieved")
                print(f"[SATELLITE] 📊 {sat_data['satellite']} Data ({sat_data.get('data_source', 'Live API')})")
                
                no2 = sat_data.get('no2', {})
                aerosol = sat_data.get('aerosol', {})
                
                if no2.get('value') is not None:
                    print(f"|-- 🚗 NO2 (Traffic/Industrial): {no2['value']:.3f} ({no2['status']})")
                else:
                    print(f"|-- 🚗 NO2: Data Unavailable")
                    
                if aerosol.get('value') is not None:
                    print(f"|-- 💨 Aerosol Index: {aerosol['value']:.2f} ({aerosol['status']})")
                else:
                    print(f"|-- 💨 Aerosol Index: Data Unavailable")
                
                print()
            else:
                print(f"[WARNING] Satellite data unavailable, continuing with air quality only")
                print()
        except Exception as e:
            print(f"[WARNING] Satellite API error: {e}")
            print(f"[INFO] Continuing with air quality data only")
            print()
    else:
        print(f"[INFO] Sentinel Hub client not initialized (check API credentials)")
        print(f"[INFO] Continuing with air quality data only")
        print()
    
    print("[PIPELINE] Step 3/4: Analyzing Anomalies...")
    result = detect_anomalies(historical_data, current_value)
    
    if result["status"] == "ERROR":
        print(f"[WARNING] Analysis failed: {result['explanation']}")
        return False
    
    print("[SUCCESS] Analysis complete.")
    
    if sat_data:
        result['satellite_data'] = sat_data
    
    print("\n[AI] 🧠 Generating Comprehensive Intelligence Report...")
    try:
        from src.ai_engine import generate_comprehensive_advisory
        from src.ai_engine import generate_fallback_advisory
        
        sensor_data = {
            "current_value": current_value,
            "status": result["status"],
            "z_score": result.get("z_score", 0),
            "baseline_mean": result.get("baseline_mean", 0),
            "baseline_std": result.get("baseline_std", 0)
        }
        
        ai_message = generate_comprehensive_advisory(sensor_data, satellite_data=sat_data)
        
        print(f"\n{'='*70}")
        print("  AI INTELLIGENCE REPORT")
        print(f"{'='*70}")
        print(f"\n{ai_message}\n")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"[WARNING] AI service failed: {e}")
        from src.ai_engine import generate_fallback_advisory
        ai_message = generate_fallback_advisory(result["status"])
        print(f"\n{'='*70}")
        print("  AI INTELLIGENCE REPORT (Fallback)")
        print(f"{'='*70}")
        print(f"\n{ai_message}\n")
        print(f"{'='*70}\n")
    
    result['ai_message'] = ai_message
    result['ai_explanation'] = ai_message
    
    save_to_json(result, current_value, timestamp)
    print_diagnostic_report(result, current_value, timestamp)
    
    print(f"\n[SYSTEM] Pipeline iteration completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    return True


def get_location_coordinates():
    """
    Get location coordinates from user input using geocoding.
    
    Returns:
        Dictionary with latitude and longitude, or None if failed
    """
    print("\n" + "=" * 70)
    print("  LOCATION SETUP")
    print("=" * 70 + "\n")
    
    use_default = input("Use default location (Hyderabad, India)? (y/n): ").strip().lower()
    
    if use_default == 'y':
        print(f"[SELECTED] Using Hyderabad, India (17.3850°N, 78.4867°E)\n")
        return {"latitude": 17.3850, "longitude": 78.4867, "name": "Hyderabad, India"}
    
    while True:
        try:
            location_name = input("Enter location (city, country): ").strip()
            
            if not location_name:
                print("[ERROR] Location cannot be empty")
                continue
            
            print(f"[INFO] Geocoding '{location_name}'...")
            
            geolocator = Nominatim(user_agent="environmental_monitoring_system")
            location = geolocator.geocode(location_name, timeout=10)
            
            if location:
                print(f"[SUCCESS] Found: {location.address}")
                print(f"[COORDINATES] {location.latitude:.4f}°N, {location.longitude:.4f}°E\n")
                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "name": location.address
                }
            else:
                print(f"[ERROR] Location '{location_name}' not found. Try again.")
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"[ERROR] Geocoding service error: {e}")
            print("[INFO] Try again or use default location")
        except KeyboardInterrupt:
            print("\n[SYSTEM] Location setup cancelled")
            return None


def main():
    """Main execution with continuous monitoring loop."""
    
    print_banner()
    print(f"[SYSTEM] Starting Early Warning Intelligence Layer...")
    print(f"[CONFIG] Target City: {config.TARGET_CITY}")
    print(f"[CONFIG] Parameter: {config.PARAMETER}")
    print(f"[CONFIG] OpenAQ API: {'Configured' if config.API_KEY else 'Not configured'}")
    
    print(f"[CONFIG] Initializing Sentinel Hub client...")
    sentinel_client = SentinelClient()
    if sentinel_client.client_id and sentinel_client.client_secret:
        print(f"[CONFIG] Sentinel Hub: Configured")
    else:
        print(f"[CONFIG] Sentinel Hub: Not configured (will skip satellite data)")
    print()
    
    location_coords = get_location_coordinates()
    if not location_coords:
        print("[INFO] Location setup failed. Exiting...")
        return
    
    selected_location_id = select_sensor_interactively(location_coords)
    
    if selected_location_id is None:
        print("[INFO] No sensor selected. Exiting...")
        return
    
    iteration = 0
    while True:
        try:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"  ITERATION #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
            print(f"  Location: {location_coords.get('name', 'Unknown')}")
            print(f"{'='*70}\n")
            
            run_pipeline(
                location_id=selected_location_id,
                sentinel_client=sentinel_client,
                location_coords=location_coords
            )
            
            print(f"\n💤 Sleeping for 5 minutes... Press Ctrl+C to stop.")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Received shutdown signal (Ctrl+C)")
            print("[SYSTEM] Gracefully shutting down...")
            print("=" * 70)
            print("  EARLY WARNING INTELLIGENCE LAYER STOPPED")
            print("=" * 70)
            break
            
        except Exception as e:
            print(f"\n[ERROR] Unexpected error in pipeline: {e}")
            print("[SYSTEM] Continuing to next iteration after error...")
            time.sleep(60)


if __name__ == "__main__":
    main()