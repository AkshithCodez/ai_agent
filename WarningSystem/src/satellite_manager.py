"""
Sentinel Hub API Manager
Real-time satellite data integration for NDVI/NDWI indices and imagery.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path


class SentinelClient:
    """
    Client for interacting with Sentinel Hub API.
    Handles OAuth2 authentication, statistical data, and imagery retrieval.
    """
    
    BASE_URL = "https://services.sentinel-hub.com"
    
    def __init__(self):
        """Initialize the Sentinel Hub client with credentials from environment."""
        self.client_id = os.getenv("SENTINEL_CLIENT_ID")
        self.client_secret = os.getenv("SENTINEL_CLIENT_SECRET")
        self.token = None
        
        if not self.client_id or not self.client_secret:
            print("[WARNING] Sentinel Hub credentials not found in environment variables.")
            print("[INFO] Set SENTINEL_CLIENT_ID and SENTINEL_CLIENT_SECRET in .env file.")
    
    def _get_token(self) -> Optional[str]:
        """
        Authenticate with Sentinel Hub using OAuth2 client credentials flow.
        
        Returns:
            Access token string, or None if authentication fails
        """
        if not self.client_id or not self.client_secret:
            return None
        
        try:
            url = f"{self.BASE_URL}/oauth/token"
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.token = token_data.get("access_token")
            
            print("[SENTINEL] ✓ OAuth2 authentication successful")
            return self.token
            
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Sentinel Hub authentication failed: {e}")
            return None
    
    def _create_bbox(self, lat: float, lon: float, size_km: float = 1.0) -> list:
        """
        Create a bounding box around a coordinate point.
        
        Args:
            lat: Latitude
            lon: Longitude
            size_km: Size of the box in kilometers (default 1km)
        
        Returns:
            Bounding box as [min_lon, min_lat, max_lon, max_lat]
        """
        # Approximate degrees per km (varies by latitude)
        # At equator: 1 degree ≈ 111 km
        # This is a simplified calculation
        lat_offset = (size_km / 111.0) / 2
        lon_offset = (size_km / (111.0 * abs(max(min(lat, 89), -89)) / 90)) / 2
        
        return [
            lon - lon_offset,  # min_lon
            lat - lat_offset,  # min_lat
            lon + lon_offset,  # max_lon
            lat + lat_offset   # max_lat
        ]
    
    def get_geo_stats(self, lat: float, lon: float) -> Dict:
        """
        Fetch NDVI and NDWI statistics for a location using Statistical API.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
        
        Returns:
            Dictionary with NDVI, NDWI values and status
        """
        # Get authentication token
        if not self.token:
            token = self._get_token()
            if not token:
                return self._fallback_stats()
        
        try:
            url = f"{self.BASE_URL}/api/v1/statistics"
            
            # Create bounding box (1km around point)
            bbox = self._create_bbox(lat, lon, size_km=1.0)
            
            # Date range: last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Evalscript to calculate NDVI and NDWI
            evalscript = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["B03", "B04", "B08"],
                        units: "DN"
                    }],
                    output: [
                        {
                            id: "ndvi",
                            bands: 1
                        },
                        {
                            id: "ndwi",
                            bands: 1
                        }
                    ]
                };
            }
            
            function evaluatePixel(sample) {
                // NDVI = (NIR - Red) / (NIR + Red)
                let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
                
                // NDWI = (Green - NIR) / (Green + NIR)
                let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
                
                return {
                    ndvi: [ndvi],
                    ndwi: [ndwi]
                };
            }
            """
            
            # Request payload
            payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {
                            "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                        }
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                                "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                            },
                            "maxCloudCoverage": 20
                        }
                    }]
                },
                "aggregation": {
                    "timeRange": {
                        "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                        "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                    },
                    "aggregationInterval": {
                        "of": "P1D"
                    },
                    "evalscript": evalscript
                },
                "calculations": {
                    "default": {}
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract and average NDVI/NDWI values
            ndvi_values = []
            ndwi_values = []
            
            for item in data.get("data", []):
                outputs = item.get("outputs", {})
                if "ndvi" in outputs and "ndwi" in outputs:
                    ndvi_stats = outputs["ndvi"].get("bands", {}).get("B0", {}).get("stats", {})
                    ndwi_stats = outputs["ndwi"].get("bands", {}).get("B0", {}).get("stats", {})
                    
                    if "mean" in ndvi_stats:
                        ndvi_values.append(ndvi_stats["mean"])
                    if "mean" in ndwi_stats:
                        ndwi_values.append(ndwi_stats["mean"])
            
            # Calculate averages
            ndvi = sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0.0
            ndwi = sum(ndwi_values) / len(ndwi_values) if ndwi_values else 0.0
            
            # Determine status
            ndvi_status = self._get_ndvi_status(ndvi)
            ndwi_status = self._get_ndwi_status(ndwi)
            
            print(f"[SENTINEL] ✓ Retrieved live statistics (30-day average)")
            
            return {
                "satellite": "Sentinel-2A",
                "product": "L2A_Surface_Reflectance",
                "data_source": "Live API",
                "time_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "water": {
                    "index": "NDWI",
                    "value": round(ndwi, 3),
                    "status": ndwi_status
                },
                "land": {
                    "index": "NDVI",
                    "value": round(ndvi, 3),
                    "status": ndvi_status
                }
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Sentinel Hub Statistical API failed: {e}")
            return self._fallback_stats()
        except Exception as e:
            print(f"[WARNING] Error processing satellite statistics: {e}")
            return self._fallback_stats()
    
    def get_satellite_image(self, lat: float, lon: float) -> Optional[str]:
        """
        Fetch true-color satellite image for a location using Process API.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
        
        Returns:
            Path to saved image file, or None if failed
        """
        # Get authentication token
        if not self.token:
            token = self._get_token()
            if not token:
                print("[WARNING] Cannot fetch satellite image without authentication")
                return None
        
        try:
            url = f"{self.BASE_URL}/api/v1/process"
            
            # Create bounding box (1km around point)
            bbox = self._create_bbox(lat, lon, size_km=1.0)
            
            # Date range: last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Evalscript for true-color image
            evalscript = """
            //VERSION=3
            function setup() {
                return {
                    input: ["B04", "B03", "B02"],
                    output: {
                        bands: 3,
                        sampleType: "AUTO"
                    }
                };
            }
            
            function evaluatePixel(sample) {
                return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
            }
            """
            
            # Request payload
            payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {
                            "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                        }
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                                "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                            },
                            "maxCloudCoverage": 20
                        }
                    }]
                },
                "output": {
                    "width": 512,
                    "height": 512,
                    "responses": [{
                        "identifier": "default",
                        "format": {
                            "type": "image/png"
                        }
                    }]
                },
                "evalscript": evalscript
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "image/png"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Create visuals directory if it doesn't exist
            visuals_dir = Path("data/visuals")
            visuals_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image
            image_path = visuals_dir / "sat_image.png"
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            print(f"[SENTINEL] ✓ Satellite image saved to {image_path}")
            return str(image_path)
            
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Sentinel Hub Process API failed: {e}")
            return None
        except Exception as e:
            print(f"[WARNING] Error saving satellite image: {e}")
            return None
    
    def _get_ndvi_status(self, ndvi: float) -> str:
        """Determine NDVI status based on value."""
        if ndvi < 0.2:
            return "POOR_VEGETATION"
        elif ndvi < 0.35:
            return "MODERATE_VEGETATION"
        else:
            return "GOOD_VEGETATION"
    
    def _get_ndwi_status(self, ndwi: float) -> str:
        """Determine NDWI status based on value."""
        if ndwi > 0.3:
            return "HEALTHY"
        elif ndwi > 0.1:
            return "MODERATE"
        elif ndwi >= 0.0:
            return "STRESSED"
        else:
            return "DROUGHT_TURBID"
    
    def _fallback_stats(self) -> Dict:
        """Return fallback data structure when API is unavailable."""
        return {
            "satellite": "Sentinel-2A",
            "product": "L2A_Surface_Reflectance",
            "data_source": "Unavailable",
            "water": {
                "index": "NDWI",
                "value": None,
                "status": "DATA_UNAVAILABLE"
            },
            "land": {
                "index": "NDVI",
                "value": None,
                "status": "DATA_UNAVAILABLE"
            }
        }
