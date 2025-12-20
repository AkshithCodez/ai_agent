"""
Sentinel-2A Satellite Data Simulation Module
Simulates spectral indices for Water and Land quality monitoring.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Tuple


def _generate_ndwi() -> Tuple[float, str]:
    """
    Generate simulated NDWI (Normalized Difference Water Index) value.
    
    NDWI measures water content and health:
    - Range: -0.2 to 0.4
    - Higher values (>0.3) indicate healthy water bodies
    - Lower values (<0.0) indicate drought or turbid water
    
    Returns:
        Tuple of (ndwi_value, status_string)
    """
    # Generate random NDWI value between -0.2 and 0.4
    ndwi = round(random.uniform(-0.2, 0.4), 3)
    
    # Determine status based on NDWI value
    if ndwi > 0.3:
        status = "HEALTHY"
    elif ndwi > 0.1:
        status = "MODERATE"
    elif ndwi >= 0.0:
        status = "STRESSED"
    else:
        status = "DROUGHT_TURBID"
    
    return ndwi, status


def _generate_ndvi() -> Tuple[float, str]:
    """
    Generate simulated NDVI (Normalized Difference Vegetation Index) value.
    
    NDVI measures vegetation health and density:
    - Range: 0.1 to 0.5
    - Low (0.1-0.2) indicates concrete/urbanization (typical for Delhi)
    - Moderate (0.2-0.35) indicates sparse vegetation
    - High (>0.35) indicates good vegetation cover
    
    Returns:
        Tuple of (ndvi_value, status_string)
    """
    # Generate random NDVI value between 0.1 and 0.5
    ndvi = round(random.uniform(0.1, 0.5), 3)
    
    # Determine status based on NDVI value
    if ndvi < 0.2:
        status = "POOR_VEGETATION"
    elif ndvi < 0.35:
        status = "MODERATE_VEGETATION"
    else:
        status = "GOOD_VEGETATION"
    
    return ndvi, status


def _generate_last_pass_timestamp() -> str:
    """
    Generate a simulated satellite pass timestamp.
    
    Sentinel-2A satellites pass every 5-10 days.
    This simulates a pass that occurred 2-3 days ago.
    
    Returns:
        ISO 8601 formatted timestamp string
    """
    # Generate random number of days ago (2-3 days)
    days_ago = random.uniform(2.0, 3.0)
    
    # Calculate the timestamp
    last_pass = datetime.now() - timedelta(days=days_ago)
    
    # Format as ISO 8601 with 'Z' suffix (UTC)
    return last_pass.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_sentinel_indices(lat: float, lon: float) -> Dict:
    """
    Fetch simulated Sentinel-2A satellite spectral indices for a given location.
    
    This function simulates a connection to the Sentinel Hub API and returns
    spectral indices for water and land quality monitoring.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
    
    Returns:
        Dictionary containing:
        - satellite: Satellite name
        - product: Product type
        - last_pass: ISO 8601 timestamp of last satellite pass
        - water: Dictionary with NDWI index, value, and status
        - land: Dictionary with NDVI index, value, and status
    
    Example:
        >>> data = fetch_sentinel_indices(28.6139, 77.2090)
        >>> print(data['water']['status'])
        'STRESSED'
    """
    # Generate spectral indices
    ndwi_value, ndwi_status = _generate_ndwi()
    ndvi_value, ndvi_status = _generate_ndvi()
    last_pass = _generate_last_pass_timestamp()
    
    # Construct response
    return {
        "satellite": "Sentinel-2A",
        "product": "L2A_Surface_Reflectance",
        "last_pass": last_pass,
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "water": {
            "index": "NDWI",
            "value": ndwi_value,
            "status": ndwi_status
        },
        "land": {
            "index": "NDVI",
            "value": ndvi_value,
            "status": ndvi_status
        }
    }
