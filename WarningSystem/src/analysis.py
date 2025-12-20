"""
Intelligence Analysis Module
Implements Z-Score anomaly detection for air quality monitoring.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from . import config


def detect_anomalies(history_list: List[float], current_value: float) -> Dict:
    """
    Detects anomalies using Z-Score statistical analysis.
    
    Args:
        history_list: List of historical measurements for baseline calculation
        current_value: Current measurement to evaluate
    
    Returns:
        Dictionary containing:
        - status: Alert level (NORMAL, WARNING, DISTRESS, CRITICAL)
        - severity_score: Numeric score (0-3)
        - z_score: Calculated Z-Score value
        - explanation: Human-readable explanation
        - baseline_mean: Mean of historical data
        - baseline_std: Standard deviation of historical data
    """
    
    # Validate inputs
    if not history_list or len(history_list) < 2:
        return {
            "status": "ERROR",
            "severity_score": -1,
            "z_score": None,
            "explanation": "Insufficient historical data for baseline calculation (need at least 2 points).",
            "baseline_mean": None,
            "baseline_std": None
        }
    
    if current_value is None:
        return {
            "status": "ERROR",
            "severity_score": -1,
            "z_score": None,
            "explanation": "Current value is None. Cannot perform analysis.",
            "baseline_mean": None,
            "baseline_std": None
        }
    
    try:
        # Step A: Convert to Pandas Series
        historical_series = pd.Series(history_list)
        
        # Step B: Calculate Rolling Mean and Standard Deviation
        # Using the entire dataset for baseline (not rolling window)
        baseline_mean = historical_series.mean()
        baseline_std = historical_series.std()
        
        # Handle edge case where std is 0 (all values identical)
        if baseline_std == 0 or pd.isna(baseline_std):
            if abs(current_value - baseline_mean) < 0.01:  # Essentially equal
                return {
                    "status": "NORMAL",
                    "severity_score": 0,
                    "z_score": 0.0,
                    "explanation": "All baseline values are identical. Current value matches baseline.",
                    "baseline_mean": float(baseline_mean),
                    "baseline_std": 0.0
                }
            else:
                return {
                    "status": "CRITICAL",
                    "severity_score": 3,
                    "z_score": float('inf'),
                    "explanation": "All baseline values are identical, but current value differs significantly.",
                    "baseline_mean": float(baseline_mean),
                    "baseline_std": 0.0
                }
        
        # Step C: Calculate Z-Score
        z_score = (current_value - baseline_mean) / baseline_std
        
        # Step D: Compare Z-Score to Thresholds
        abs_z_score = abs(z_score)
        
        if abs_z_score >= config.THRESHOLDS["HIGH_CRITICAL"]:
            status = "CRITICAL"
            severity_score = 3
        elif abs_z_score >= config.THRESHOLDS["MEDIUM_DISTRESS"]:
            status = "DISTRESS"
            severity_score = 2
        elif abs_z_score >= config.THRESHOLDS["LOW_WARNING"]:
            status = "WARNING"
            severity_score = 1
        else:
            status = "NORMAL"
            severity_score = 0
        
        # Step E: Generate Explanation
        direction = "above" if z_score > 0 else "below"
        explanation = (
            f"Value is {abs_z_score:.2f} standard deviations {direction} normal. "
            f"Current: {current_value:.2f}, Baseline Mean: {baseline_mean:.2f}, "
            f"Baseline Std: {baseline_std:.2f}"
        )
        
        return {
            "status": status,
            "severity_score": severity_score,
            "z_score": float(z_score),
            "explanation": explanation,
            "baseline_mean": float(baseline_mean),
            "baseline_std": float(baseline_std)
        }
    
    except Exception as e:
        return {
            "status": "ERROR",
            "severity_score": -1,
            "z_score": None,
            "explanation": f"Analysis failed: {str(e)}",
            "baseline_mean": None,
            "baseline_std": None
        }
