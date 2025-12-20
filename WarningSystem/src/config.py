
"""
Configuration module for the Early Warning Intelligence Layer.
Defines constants for API endpoints, target parameters, and alert thresholds.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Target Configuration
TARGET_CITY = "Delhi"
PARAMETER = "pm25"

# API Configuration
API_KEY = os.getenv("OPENAQ_API_KEY")  # Load API key from environment


# Z-Score Thresholds for Alert Levels
THRESHOLDS = {
    "LOW_WARNING": 1.5,      # Moderate deviation from baseline
    "MEDIUM_DISTRESS": 2.0,  # Significant deviation requiring attention
    "HIGH_CRITICAL": 3.0     # Critical deviation requiring immediate action
}

# Data Collection Parameters
HISTORICAL_LIMIT = 100  # Number of historical data points for baseline
LIVE_LIMIT = 1          # Number of recent data points to fetch

# API Request Timeout (seconds)
REQUEST_TIMEOUT = 10
