"""
Sentinel-5P Satellite Data Simulation Module
Simulates air quality indices for pollution monitoring.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Tuple


def _generate_no2() -> Tuple[float, str]:
    """
    Generate simulated NO2 (Nitrogen Dioxide) value.
    
    NO2 measures nitrogen dioxide concentration:
    - Range: 0.0 to 0.5 (mol/m2 for satellite)
    - Higher values indicate more traffic/industrial emissions
    
    Returns:
        Tuple of (no2_value, status_string)
    """
    no2 = round(random.uniform(0.0, 0.3), 3)
    
    if no2 > 0.2:
        status = "HIGH_POLLUTION"
    elif no2 > 0.1:
        status = "MODERATE_POLLUTION"
    elif no2 > 0.05:
        status = "LOW_POLLUTION"
    else:
        status = "CLEAN"
    
    return no2, status


def _generate_aerosol_index() -> Tuple[float, str]:
    """
    Generate simulated Aerosol Index value.
    
    Aerosol Index measures particulate matter in the atmosphere:
    - Range: -2.0 to 5.0
    - Positive values indicate absorbing aerosols (dust/pollution)
    - Negative values indicate non-absorbing particles
    
    Returns:
        Tuple of (ai_value, status_string)
    """
    ai = round(random.uniform(-1.0, 3.0), 2)
    
    if ai > 2.0:
        status = "SEVERE_AEROSOL"
    elif ai > 1.0:
        status = "MODERATE_AEROSOL"
    elif ai > 0.0:
        status = "LIGHT_AEROSOL"
    else:
        status = "CLEAR"
    
    return ai, status


def _generate_last_pass_timestamp() -> str:
    """
    Generate a simulated satellite pass timestamp.
    
    Sentinel-5P satellites pass daily.
    This simulates a pass that occurred 1-2 days ago.
    
    Returns:
        ISO 8601 formatted timestamp string
    """
    days_ago = random.uniform(1.0, 2.0)
    last_pass = datetime.now() - timedelta(days=days_ago)
    return last_pass.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_sentinel_air_quality(lat: float, lon: float) -> Dict:
    """
    Fetch simulated Sentinel-5P satellite air quality indices for a given location.
    
    This function simulates a connection to the Sentinel Hub API and returns
    air quality indices for pollution monitoring.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
    
    Returns:
        Dictionary containing:
        - satellite: Satellite name
        - product: Product type
        - last_pass: ISO 8601 timestamp of last satellite pass
        - no2: Dictionary with NO2 index, value, and status
        - aerosol: Dictionary with Aerosol Index, value, and status
    """
    no2_value, no2_status = _generate_no2()
    ai_value, ai_status = _generate_aerosol_index()
    last_pass = _generate_last_pass_timestamp()
    
    return {
        "satellite": "Sentinel-5P",
        "product": "L2__NO2___",
        "last_pass": last_pass,
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "no2": {
            "index": "NO2",
            "value": no2_value,
            "status": no2_status
        },
        "aerosol": {
            "index": "AEROSOL_INDEX",
            "value": ai_value,
            "status": ai_status
        }
    }