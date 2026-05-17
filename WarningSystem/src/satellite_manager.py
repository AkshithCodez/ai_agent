"""
Sentinel Hub API Manager - Sentinel-5P Air Quality
Real-time satellite air quality data integration for NO2 and Aerosol Index.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv


class SentinelClient:
    """
    Client for interacting with Sentinel Hub API for Sentinel-5P air quality data.
    Handles OAuth2 authentication, statistical data, and imagery retrieval.
    """
    
    BASE_URL = "https://services.sentinel-hub.com"
    
    def __init__(self):
        """Initialize the Sentinel Hub client with credentials from environment."""
        # Explicitly load environment variables
        load_dotenv()
        
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
    
    def get_air_quality_stats(self, lat: float, lon: float) -> Dict:
        """
        Fetch NO2 and Aerosol Index statistics for a location using Statistical API.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
        
        Returns:
            Dictionary with NO2, Aerosol Index values and status (NEVER returns None)
        """
        if not self.token:
            token = self._get_token()
            if not token:
                print("[SENTINEL] No authentication token, using fallback values")
                return self._get_fallback_values()
        
        try:
            url = f"{self.BASE_URL}/api/v1/statistics"
            
            delta = 0.01
            bbox = [lon - delta, lat - delta, lon + delta, lat + delta]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            evalscript = """
            //VERSION=3
            function setup() {
              return {
                input: ["NO2", "AER_AI", "dataMask"],
                output: [
                  {id: "no2", bands: 1},
                  {id: "aerosol", bands: 1},
                  {id: "dataMask", bands: 1}
                ]
              };
            }
            function evaluatePixel(sample) {
              return {
                no2: [sample.NO2],
                aerosol: [sample.AER_AI],
                dataMask: [sample.dataMask]
              };
            }
            """
            
            payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {
                            "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                        }
                    },
                    "data": [{
                        "type": "sentinel-5p-l2",
                        "dataFilter": {
                            "timeRange": {
                                "from": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "to": end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                            }
                        }
                    }]
                },
                "aggregation": {
                    "timeRange": {
                        "from": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "to": end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                    },
                    "aggregationInterval": {
                        "of": "P1D"
                    },
                    "resx": 1000,
                    "resy": 1000,
                    "evalscript": evalscript
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            no2_values = []
            aerosol_values = []
            
            if 'data' in data and len(data['data']) > 0:
                for item in data['data']:
                    outputs = item.get('outputs', {})
                    
                    if 'no2' in outputs:
                        no2_stats = outputs['no2'].get('bands', {}).get('B0', {}).get('stats', {})
                        if 'mean' in no2_stats:
                            no2_values.append(no2_stats['mean'])
                    
                    if 'aerosol' in outputs:
                        aerosol_stats = outputs['aerosol'].get('bands', {}).get('B0', {}).get('stats', {})
                        if 'mean' in aerosol_stats:
                            aerosol_values.append(aerosol_stats['mean'])
            
            if no2_values and aerosol_values:
                no2 = sum(no2_values) / len(no2_values)
                aerosol = sum(aerosol_values) / len(aerosol_values)
                print(f"[SENTINEL] ✓ Retrieved live air quality statistics (NO2: {no2:.3f}, AI: {aerosol:.2f})")
            else:
                print("[SENTINEL] No satellite data in response, using fallback values")
                return self._get_fallback_values()
            
            no2_status = self._get_no2_status(no2)
            aerosol_status = self._get_aerosol_status(aerosol)
            
            return {
                "satellite": "Sentinel-5P",
                "product": "L2__NO2___",
                "data_source": "Live API",
                "time_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "no2": {
                    "index": "NO2",
                    "value": round(no2, 3),
                    "status": no2_status
                },
                "aerosol": {
                    "index": "AEROSOL_INDEX",
                    "value": round(aerosol, 2),
                    "status": aerosol_status
                }
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Sentinel Hub Statistical API failed: {e}")
            return self._get_fallback_values()
        except Exception as e:
            print(f"[WARNING] Error processing satellite statistics: {e}")
            return self._get_fallback_values()
    
    def _get_geo_stats(self, lat: float, lon: float) -> Dict:
        """Legacy method - redirects to air quality stats."""
        return self.get_air_quality_stats(lat, lon)
    
    def _get_no2_status(self, no2: float) -> str:
        """Determine NO2 status based on value."""
        if no2 > 0.2:
            return "HIGH_POLLUTION"
        elif no2 > 0.1:
            return "MODERATE_POLLUTION"
        elif no2 > 0.05:
            return "LOW_POLLUTION"
        else:
            return "CLEAN"
    
    def _get_aerosol_status(self, aerosol: float) -> str:
        """Determine Aerosol Index status based on value."""
        if aerosol > 2.0:
            return "SEVERE_AEROSOL"
        elif aerosol > 1.0:
            return "MODERATE_AEROSOL"
        elif aerosol > 0.0:
            return "LIGHT_AEROSOL"
        else:
            return "CLEAR"
    
    def _get_fallback_values(self) -> Dict:
        """Return realistic fallback data when API is unavailable."""
        return {
            "satellite": "Sentinel-5P",
            "product": "L2__NO2___",
            "data_source": "Simulated (Fallback)",
            "time_range": "Unavailable",
            "location": {
                "latitude": 0.0,
                "longitude": 0.0
            },
            "no2": {
                "index": "NO2",
                "value": 0.1,
                "status": "SIMULATED"
            },
            "aerosol": {
                "index": "AEROSOL_INDEX",
                "value": 0.5,
                "status": "SIMULATED"
            }
        }
    
    def _fallback_stats(self) -> Dict:
        """Legacy fallback method."""
        return self._get_fallback_values()