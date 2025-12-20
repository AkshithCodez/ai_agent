"""
Data Ingestion Module
Handles fetching real-time and historical air quality data from OpenAQ API.
Falls back to simulated data for demo purposes when API is unavailable.
"""

import requests
import random
import math
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from . import config


# Delhi coordinates for geo-location based sensor discovery
DELHI_LAT = 28.6139
DELHI_LON = 77.2090
SEARCH_RADIUS = 25000  # 25km radius around Delhi center


def get_active_location_id() -> Optional[int]:
    """
    Dynamically discovers an active air quality sensor near Delhi.
    Uses geospatial radius search to find recently updated sensors.
    
    Returns:
        Location ID (int) if found, None otherwise
    """
    try:
        # Use geospatial radius search around Delhi coordinates
        # This is the correct approach for OpenAQ V3 API
        # Note: V3 API does not support order_by=lastUpdated, results are sorted by distance
        params = {
            "coordinates": f"{DELHI_LAT},{DELHI_LON}",  # Comma-separated string
            "radius": SEARCH_RADIUS,  # 25km radius
            "limit": 1  # Get the closest match
        }
        
        print(f"[DISCOVERY] Searching for active sensors within {SEARCH_RADIUS/1000}km of Delhi...")

        
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
            print("[WARNING] No active sensors found near Delhi.")
            return None
        
        # Extract the location ID from the first (best) result
        location = data["results"][0]
        location_id = location.get("id")
        location_name = location.get("name", "Unknown")
        coords = location.get("coordinates", {})
        lat = coords.get("latitude", "N/A")
        lon = coords.get("longitude", "N/A")
        
        print(f"[SUCCESS] Location discovered: {location_name} (ID: {location_id})")
        print(f"[INFO] Coordinates: {lat}, {lon}")
        
        return location_id
    
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
        # OpenAQ v3 uses location-specific measurements endpoint
        measurements_url = f"https://api.openaq.org/v3/locations/{location_id}/measurements"
        
        params = {
            "parameters_id": "2",  # PM2.5 parameter ID
            "limit": limit,
            "order_by": "datetime",
            "sort": "desc"
        }
        
        print(f"[INGESTION] Fetching {limit} historical data points from location {location_id}...")
        
        # Prepare headers with API key if available
        headers = {}
        if config.API_KEY:
            headers["X-API-Key"] = config.API_KEY
        
        response = requests.get(
            measurements_url,
            params=params,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            print("[WARNING] No historical data found in API response. Using simulated data.")
            return generate_simulated_data(limit)
        
        # Extract values from results (v3 structure)
        values = []
        for result in data["results"]:
            if "value" in result and result["value"] is not None:
                values.append(float(result["value"]))
        
        print(f"[SUCCESS] Retrieved {len(values)} historical data points from API.")
        return values
    
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
        measurements_url = f"https://api.openaq.org/v3/locations/{location_id}/measurements"
        
        params = {
            "parameters_id": "2",  # PM2.5 parameter ID
            "limit": config.LIVE_LIMIT,
            "order_by": "datetime",
            "sort": "desc"
        }
        
        print(f"[INGESTION] Fetching live data from location {location_id}...")
        
        # Prepare headers with API key if available
        headers = {}
        if config.API_KEY:
            headers["X-API-Key"] = config.API_KEY
        
        response = requests.get(
            measurements_url,
            params=params,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            print("[WARNING] No live data found in API response. Using simulated data.")
            baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 150.0
            return generate_simulated_live_data(baseline_mean)
        
        result = data["results"][0]
        value = float(result["value"])
        # v3 API has different timestamp structure
        timestamp = result.get("datetime", {}).get("utc", "Unknown") if isinstance(result.get("datetime"), dict) else result.get("datetime", "Unknown")
        
        print(f"[SUCCESS] Retrieved live data from API: {value} at {timestamp}")
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

