"""
Early Warning Intelligence Layer - Main Execution Script
Orchestrates the real-time air quality monitoring pipeline.
Runs continuously as a background service.
"""

import json
import time
import os
import sys
from pathlib import Path
from src.ingestion import fetch_historical_data, fetch_live_data, discover_available_sensors, convert_to_ist
from src.analysis import detect_anomalies
from src.ai_adapter import get_ai_explanation
from src import config
from datetime import datetime


def save_to_json(result: dict, current_value: float, timestamp: str):
    """
    Saves analysis results to JSON file for dashboard integration.
    
    Args:
        result: Analysis result dictionary from detect_anomalies
        current_value: Current measurement value
        timestamp: Timestamp of the measurement (in IST format)
    """
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Prepare output data
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
        "ai_explanation": result.get("ai_explanation", "N/A"),
        "ai_message": result.get("ai_message", "N/A")  # Comprehensive advisory
    }
    
    # Write to file (overwrite mode)
    output_file = data_dir / "latest_alert.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"[EXPORT] Analysis saved to {output_file}")


def print_banner():
    """Prints the system startup banner."""
    print("=" * 70)
    print("  EARLY WARNING INTELLIGENCE LAYER")
    print("  Environmental Monitoring System v1.0")
    print("  Background Service Mode")
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
    
    # Status with color indicators
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


def select_sensor_interactively():
    """
    Displays available sensors and prompts user to select one.
    
    Returns:
        Selected location ID (int), or None if no sensors available
    """
    print("\n" + "=" * 70)
    print("  SENSOR SELECTION")
    print("=" * 70 + "\n")
    
    # Discover available sensors
    sensors = discover_available_sensors()
    
    if not sensors or len(sensors) == 0:
        print("[WARNING] No fresh sensors found.")
        print("[INFO] The system will use simulated data.\n")
        return None
    
    # Display sensor list
    print(f"Found {len(sensors)} fresh sensor(s):\n")
    for i, sensor in enumerate(sensors, 1):
        print(f"{i}. ID: {sensor['id']:5} | {sensor['name']:45} | Last Update: {sensor['last_updated_ist']}")
    
    # Get user selection
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


def run_pipeline(location_id=None):
    """
    Executes a single iteration of the monitoring pipeline.
    
    Args:
        location_id: Optional location ID to monitor. If None, auto-discovers.
    
    Returns:
        True if successful, False otherwise.
    """
    # Step 1: Fetch Historical Data for Baseline
    print("[PIPELINE] Step 1/3: Establishing Baseline...")
    historical_data = fetch_historical_data(limit=config.HISTORICAL_LIMIT, location_id=location_id)
    
    if not historical_data:
        print("[WARNING] Failed to establish baseline. Skipping this iteration.")
        return False
    
    print(f"[SUCCESS] Baseline established with {len(historical_data)} data points.")
    print()
    
    # Step 2: Fetch Live Data
    print("[PIPELINE] Step 2/3: Fetching Live Data...")
    current_value, timestamp = fetch_live_data(historical_data, location_id=location_id)
    
    if current_value is None:
        print("[WARNING] Failed to fetch live data. Skipping this iteration.")
        return False
    
    print(f"[SUCCESS] Live data retrieved: {current_value} µg/m³")
    print()
    
    # Step 3: Perform Anomaly Detection
    print("[PIPELINE] Step 3/3: Analyzing Anomalies...")
    result = detect_anomalies(historical_data, current_value)
    
    if result["status"] == "ERROR":
        print(f"[WARNING] Analysis failed: {result['explanation']}")
        return False
    
    print("[SUCCESS] Analysis complete.")
    
    # Step 4: AI Intelligence Report (Comprehensive Advisory)
    print("\n[AI] 🧠 Generating Comprehensive Intelligence Report...")
    try:
        from src.ai_engine import generate_comprehensive_advisory
        from src.ai_engine import generate_fallback_advisory
        
        # Prepare sensor data for AI
        sensor_data = {
            "current_value": current_value,
            "status": result["status"],
            "z_score": result.get("z_score", 0),
            "baseline_mean": result.get("baseline_mean", 0),
            "baseline_std": result.get("baseline_std", 0)
        }
        
        ai_message = generate_comprehensive_advisory(sensor_data)
        
        print(f"\n{'='*70}")
        print("  AI INTELLIGENCE REPORT")
        print(f"{'='*70}")
        print(f"\n{ai_message}\n")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"[WARNING] AI service failed: {e}")
        # Fallback to status-based message
        from src.ai_engine import generate_fallback_advisory
        ai_message = generate_fallback_advisory(result["status"])
        print(f"\n{'='*70}")
        print("  AI INTELLIGENCE REPORT (Fallback)")
        print(f"{'='*70}")
        print(f"\n{ai_message}\n")
        print(f"{'='*70}\n")
    
    # Add AI message to result
    result['ai_message'] = ai_message
    result['ai_explanation'] = ai_message  # Keep for backward compatibility
    
    # Step 5: Save to JSON for Dashboard
    save_to_json(result, current_value, timestamp)
    
    # Step 6: Display Diagnostic Report
    print_diagnostic_report(result, current_value, timestamp)
    
    print(f"\n[SYSTEM] Pipeline iteration completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    return True


def main():
    """Main execution with continuous monitoring loop."""
    
    # System Initialization
    print_banner()
    print(f"[SYSTEM] Starting Early Warning Intelligence Layer...")
    print(f"[CONFIG] Target City: {config.TARGET_CITY}")
    print(f"[CONFIG] Parameter: {config.PARAMETER}")
    print(f"[CONFIG] API Key: {'Configured ✓' if config.API_KEY else 'Not configured (using simulated data)'}")
    print()
    
    # Interactive sensor selection
    selected_location_id = select_sensor_interactively()
    
    if selected_location_id is None:
        print("[INFO] No sensor selected. Exiting...")
        return
    
    # Continuous monitoring loop
    iteration = 0
    while True:
        try:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"  ITERATION #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
            print(f"{'='*70}\n")
            
            # Run the pipeline with selected sensor
            run_pipeline(location_id=selected_location_id)
            
            # Sleep for 5 minutes
            print(f"\n💤 Sleeping for 5 minutes... Press Ctrl+C to stop.")
            time.sleep(300)  # 5 minutes = 300 seconds
            
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
            time.sleep(60)  # Wait 1 minute before retrying after error


if __name__ == "__main__":
    main()
