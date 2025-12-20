"""
Data Ingestion Module
Handles fetching real-time and historical air quality data from OpenAQ API.
Falls back to simulated data for demo purposes when API is unavailable.
"""

import requests
import random
import math
from typing import List, Tuple, Optional
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateutil_parser
from . import config


# Delhi coordinates for geo-location based sensor discovery
DELHI_LAT = 28.6139
DELHI_LON = 77.2090
SEARCH_RADIUS = 25000  # 25km radius around Delhi center


def get_active_location_id() -> Optional[int]:
    """
    Dynamically discovers an active air quality sensor near Delhi with freshness validation.
    Uses geospatial radius search and validates that sensors have data from the last 24 hours.
    
    Returns:
        Location ID (int) if a fresh sensor is found, None otherwise
    """
    try:
        # Step A: Search for candidate sensors
        # Fetch top 10 candidates to validate freshness
        params = {
            "coordinates": f"{DELHI_LAT},{DELHI_LON}",  # Comma-separated string
            "radius": 10000,  # 10km radius for better coverage
            "limit": 10  # Get top 10 candidates for freshness validation
        }
        
        print(f"[DISCOVERY] Searching for sensors within 10km of Delhi...")
        
        # Prepare headers with API key if available
        headers = {}
        if config.API_KEY:
            headers["X-API-Key"] = config.API_KEY
        
        response = requests.get(
            "https://api.openaq.org/v3/locations",
            params=params,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            print("[WARNING] No sensors found near Delhi.")
            return None
        
        # Step B: Validate freshness (24-hour rule)
        print(f"[VALIDATION] Checking freshness of {len(data['results'])} candidates...")
        
        current_time = datetime.now(timezone.utc)
        freshness_threshold = timedelta(hours=24)
        
        for location in data["results"]:
            location_id = location.get("id")
            location_name = location.get("name", "Unknown")
            coords = location.get("coordinates", {})
            lat = coords.get("latitude", "N/A")
            lon = coords.get("longitude", "N/A")
            
            # Extract the last update timestamp
            datetime_last = location.get("datetimeLast")
            
            if datetime_last is None:
                print(f"[SKIP] {location_name} (ID: {location_id}) - No timestamp available")
                continue
            
            # Parse the timestamp (it's a dict with 'utc' and 'local' keys)
            if isinstance(datetime_last, dict):
                timestamp_str = datetime_last.get("utc")
            else:
                timestamp_str = datetime_last
            
            if not timestamp_str:
                print(f"[SKIP] {location_name} (ID: {location_id}) - Invalid timestamp")
                continue
            
            try:
                # Parse the UTC timestamp
                sensor_timestamp = dateutil_parser.parse(timestamp_str)
                
                # Ensure it's timezone-aware
                if sensor_timestamp.tzinfo is None:
                    sensor_timestamp = sensor_timestamp.replace(tzinfo=timezone.utc)
                
                # Calculate time difference
                time_diff = current_time - sensor_timestamp
                
                # Check if data is fresh (within 24 hours)
                if time_diff < freshness_threshold:
                    print(f"[SUCCESS] Found fresh sensor: {location_name} (ID: {location_id})")
                    print(f"[INFO] Last updated: {timestamp_str} ({time_diff.total_seconds() / 3600:.1f} hours ago)")
                    print(f"[INFO] Coordinates: {lat}, {lon}")
                    return location_id
                else:
                    hours_ago = time_diff.total_seconds() / 3600
                    print(f"[SKIP] Stale sensor: {location_name} (ID: {location_id}) - Last updated {hours_ago:.1f} hours ago")
            
            except (ValueError, TypeError) as e:
                print(f"[SKIP] {location_name} (ID: {location_id}) - Failed to parse timestamp: {e}")
                continue
        
        # Step C: No fresh sensor found
        print("[WARNING] No sensors found with data from the last 24 hours.")
        print("[INFO] Switching to Simulation Mode.")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] Failed to discover location: {e}")
        return None
    
    except (KeyError, ValueError) as e:
        print(f"[WARNING] Failed to parse location response: {e}")
        return None



def generate_simulated_data(count: int, base_mean: float = 150.0, base_std: float = 40.0) -> List[float]:
    """
    Generates simulated PM2.5 data for demo purposes.
    Uses realistic values based on Delhi's typical air quality patterns.
    
    Args:
        count: Number of data points to generate
        base_mean: Base mean for normal conditions (default: 150 µg/m³)
        base_std: Base standard deviation (default: 40 µg/m³)
    
    Returns:
        List of simulated PM2.5 values
    """
    print(f"[SIMULATION] Generating {count} simulated data points...")
    
    # Generate baseline data with some variation
    values = []
    for i in range(count):
        # Add some temporal variation (simulating day/night cycles)
        time_factor = 1 + 0.3 * math.sin(i * 0.1)
        value = random.gauss(base_mean * time_factor, base_std)
        # Ensure non-negative values
        value = max(0, value)
        values.append(value)

    
    print(f"[SIMULATION] Generated {len(values)} simulated data points (mean: {sum(values)/len(values):.2f})")
    return values


def generate_simulated_live_data(baseline_mean: float = 150.0, anomaly_probability: float = 0.3) -> Tuple[float, str]:
    """
    Generates a simulated live data point, with a chance of being anomalous.
    
    Args:
        baseline_mean: Mean value for normal conditions
        anomaly_probability: Probability of generating an anomalous value (0-1)
    
    Returns:
        Tuple of (value, timestamp)
    """
    timestamp = datetime.now().isoformat()
    
    if random.random() < anomaly_probability:
        # Generate anomalous value (spike)
        anomaly_type = random.choice(['high', 'low'])
        if anomaly_type == 'high':
            # High anomaly (2-4 standard deviations above mean)
            value = baseline_mean + random.uniform(80, 160)
        else:
            # Low anomaly (unusually clean air)
            value = baseline_mean * random.uniform(0.2, 0.4)
    else:
        # Normal value
        value = random.gauss(baseline_mean, 40)
    
    value = max(0, value)
    print(f"[SIMULATION] Generated live data point: {value:.2f} µg/m³")
    return value, timestamp



def fetch_historical_data(limit: int = 100) -> List[float]:
    """
    Fetches historical air quality data to establish a baseline.
    Falls back to simulated data if API is unavailable.
    
    Args:
        limit: Number of historical data points to retrieve (default: 100)
    
    Returns:
        List of float values representing historical measurements.
        Returns simulated data if API call fails.
    """
    try:
        # Step 1: Discover active location near Delhi
        location_id = get_active_location_id()
        
        if location_id is None:
            print("[WARNING] No location ID available. Using simulated data.")
            return generate_simulated_data(limit)
        
        # Step 2: Fetch measurements from the discovered location
        # OpenAQ v3 uses /locations/{id}/latest for latest measurements
        latest_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
        
        print(f"[INGESTION] Fetching latest measurements from location {location_id}...")
        
        # Prepare headers with API key if available
        headers = {}
        if config.API_KEY:
            headers["X-API-Key"] = config.API_KEY
        
        response = requests.get(
            latest_url,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            print("[WARNING] No historical data found in API response. Using simulated data.")
            return generate_simulated_data(limit)
        
        # Extract values from results - /latest returns current readings for each parameter
        # We'll use the available data and simulate the rest to reach the requested limit
        values = []
        for result in data["results"]:
            if "value" in result and result["value"] is not None:
                values.append(float(result["value"]))
        
        # If we got some real data but not enough, use it as baseline for simulation
        if len(values) > 0 and len(values) < limit:
            print(f"[INFO] Got {len(values)} real measurements, generating {limit - len(values)} simulated points...")
            baseline_mean = sum(values) / len(values)
            additional_values = generate_simulated_data(limit - len(values), base_mean=baseline_mean)
            values.extend(additional_values)
        elif len(values) == 0:
            print("[WARNING] No valid measurements found. Using simulated data.")
            return generate_simulated_data(limit)
        
        print(f"[SUCCESS] Retrieved {len(values)} data points (real + simulated baseline).")
        return values[:limit]  # Ensure we don't exceed the limit
    
    except requests.exceptions.Timeout:
        print("[WARNING] API request timed out. Using simulated data for demo.")
        return generate_simulated_data(limit)
    
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] API unavailable ({e}). Using simulated data for demo.")
        return generate_simulated_data(limit)
    
    except (KeyError, ValueError) as e:
        print(f"[WARNING] Failed to parse API response ({e}). Using simulated data for demo.")
        return generate_simulated_data(limit)



def fetch_live_data(baseline_values: Optional[List[float]] = None) -> Tuple[Optional[float], Optional[str]]:
    """
    Fetches the most recent air quality measurement.
    Falls back to simulated data if API is unavailable.
    
    Args:
        baseline_values: Optional baseline values to calculate realistic simulated data
    
    Returns:
        Tuple of (value, timestamp) where:
        - value: The most recent measurement (float)
        - timestamp: ISO format timestamp string
        Returns simulated data if API call fails.
    """
    try:
        # Step 1: Discover active location near Delhi
        location_id = get_active_location_id()
        
        if location_id is None:
            print("[WARNING] No location ID available. Using simulated data.")
            baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
            return generate_simulated_live_data(baseline_mean)
        
        # Step 2: Fetch latest measurement from the discovered location
        # OpenAQ v3 uses /locations/{id}/latest for latest measurements
        latest_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
        
        print(f"[INGESTION] Fetching live data from location {location_id}...")
        
        # Prepare headers with API key if available
        headers = {}
        if config.API_KEY:
            headers["X-API-Key"] = config.API_KEY
        
        response = requests.get(
            latest_url,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            print("[WARNING] No live data found in API response. Using simulated data.")
            baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
            return generate_simulated_live_data(baseline_mean)
        
        # Filter for fresh measurements (within 24 hours)
        # The /latest endpoint returns data for ALL sensors, including old ones
        current_time = datetime.now(timezone.utc)
        freshness_threshold = timedelta(hours=24)
        fresh_results = []
        
        for result in data["results"]:
            datetime_info = result.get("datetime")
            if not datetime_info:
                continue
            
            # Parse timestamp
            if isinstance(datetime_info, dict):
                timestamp_str = datetime_info.get("utc")
            else:
                timestamp_str = datetime_info
            
            if not timestamp_str:
                continue
            
            try:
                sensor_timestamp = dateutil_parser.parse(timestamp_str)
                if sensor_timestamp.tzinfo is None:
                    sensor_timestamp = sensor_timestamp.replace(tzinfo=timezone.utc)
                
                time_diff = current_time - sensor_timestamp
                
                # Only include measurements from the last 24 hours
                if time_diff < freshness_threshold:
                    fresh_results.append(result)
            except (ValueError, TypeError):
                continue
        
        if len(fresh_results) == 0:
            print("[WARNING] No fresh measurements found (all data is older than 24 hours). Using simulated data.")
            baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
            return generate_simulated_live_data(baseline_mean)
        
        # Use the first fresh measurement (ideally we'd filter for PM2.5 specifically)
        pm25_result = fresh_results[0]
        
        value = float(pm25_result["value"])
        # v3 API has different timestamp structure
        timestamp = pm25_result.get("datetime", {}).get("utc", "Unknown") if isinstance(pm25_result.get("datetime"), dict) else pm25_result.get("datetime", "Unknown")
        
        print(f"[SUCCESS] Retrieved live data from API: {value} µg/m³ at {timestamp}")
        print(f"[INFO] Using fresh measurement from sensor {pm25_result.get('sensorsId')}")
        return value, timestamp
    
    except requests.exceptions.Timeout:
        print("[WARNING] API request timed out. Using simulated data for demo.")
        baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
        return generate_simulated_live_data(baseline_mean)
    
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] API unavailable ({e}). Using simulated data for demo.")
        baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
        return generate_simulated_live_data(baseline_mean)
    
    except (KeyError, ValueError) as e:
        print(f"[WARNING] Failed to parse API response ({e}). Using simulated data for demo.")
        baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
        return generate_simulated_live_data(baseline_mean)

