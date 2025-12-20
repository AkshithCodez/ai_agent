"""
AI Adapter Module
Bridges the gap between the existing analysis system and the AI agent.
Converts simple analysis results into AI agent format for intelligent explanations.
"""

from datetime import datetime
from typing import Dict
from .ai_agent import EnvironmentalAIAgent, AnomalyInput, PollutantType, SeverityLevel


def get_ai_explanation(analysis_result: Dict, current_value: float, timestamp: str, 
                       location: str = "Delhi", pollutant: str = "pm25") -> str:
    """
    Get AI-generated explanation for pollution anomaly.
    
    Args:
        analysis_result: Result dictionary from detect_anomalies()
        current_value: Current pollutant value (µg/m³)
        timestamp: IST timestamp string
        location: Location name (default: "Delhi")
        pollutant: Pollutant type (default: "pm25")
    
    Returns:
        AI-generated explanation string
    """
    try:
        # Initialize AI agent
        agent = EnvironmentalAIAgent()
        
        # Map status to severity for context
        status = analysis_result.get("status", "NORMAL")
        
        # Extract baseline statistics
        baseline_mean = analysis_result.get("baseline_mean", current_value)
        z_score = analysis_result.get("z_score", 0.0)
        
        # Calculate deviation percentage
        if baseline_mean > 0:
            deviation_percentage = ((current_value - baseline_mean) / baseline_mean) * 100
        else:
            deviation_percentage = 0.0
        
        # Map our confidence (z-score based) to AI confidence
        # Higher absolute z-score = higher confidence in anomaly
        confidence_score = min(0.95, 0.6 + abs(z_score) * 0.1)
        
        # Convert pollutant string to enum
        try:
            pollutant_type = PollutantType[pollutant.upper()]
        except KeyError:
            pollutant_type = PollutantType.PM25  # Default to PM2.5
        
        # Create AnomalyInput for AI agent
        anomaly_input = AnomalyInput(
            timestamp=datetime.now(),  # Use current time
            location=location,
            pollutant=pollutant_type,
            current_value=current_value,
            baseline_value=baseline_mean,
            deviation_percentage=deviation_percentage,
            confidence_score=confidence_score,
            raw_data={
                "status": status,
                "z_score": z_score,
                "timestamp_ist": timestamp
            }
        )
        
        # Get AI decision
        decision = agent.process_anomaly(anomaly_input)
        
        # Format the response with full details for ALL conditions
        explanation_parts = [
            f"{'🚨' if decision.should_alert else '✅'} {decision.explanation}",
            f"\n📊 Severity: {decision.severity.value.upper()}",
            f"\n🎯 Confidence: {decision.confidence:.0%}",
        ]
        
        # Add reasoning for context
        if decision.reasoning:
            explanation_parts.append(f"\n\n🧠 Analysis:")
            explanation_parts.append(f"\n{decision.reasoning.strip()}")
        
        # Add recommended actions
        if decision.recommended_actions:
            explanation_parts.append(f"\n\n📋 Recommended Actions:")
            for i, action in enumerate(decision.recommended_actions, 1):
                explanation_parts.append(f"\n   {i}. {action}")
        
        return "".join(explanation_parts)
    
    except Exception as e:
        # Fallback to basic explanation if AI fails
        return f"AI analysis encountered an error: {e}. Manual review recommended."


def format_ai_summary(analysis_result: Dict, current_value: float) -> str:
    """
    Generate a brief AI summary for normal conditions.
    
    Args:
        analysis_result: Result dictionary from detect_anomalies()
        current_value: Current pollutant value
    
    Returns:
        Brief summary string
    """
    status = analysis_result.get("status", "NORMAL")
    
    if status == "NORMAL":
        return "✅ Air quality is within normal parameters. No health advisory needed."
    else:
        return "⚠️ Elevated pollution detected. AI analysis recommended."
