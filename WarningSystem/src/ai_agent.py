"""
AI Agent & Decision Logic for Environmental Monitoring System
Member B - Core AI reasoning and explanation system
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PollutantType(Enum):
    PM25 = "pm25"
    PM10 = "pm10"
    NO2 = "no2"
    O3 = "o3"
    SO2 = "so2"
    CO = "co"

@dataclass
class AnomalyInput:
    """Input data structure from Member C's detection system"""
    timestamp: datetime
    location: str
    pollutant: PollutantType
    current_value: float
    baseline_value: float
    deviation_percentage: float
    confidence_score: float
    raw_data: Dict

@dataclass
class AlertDecision:
    """AI Agent's decision output"""
    should_alert: bool
    severity: SeverityLevel
    explanation: str
    recommended_actions: List[str]
    confidence: float
    reasoning: str

class EnvironmentalAIAgent:
    """
    Core AI Agent that processes anomalies and makes alert decisions
    """
    
    def __init__(self):
        self.severity_thresholds = {
            PollutantType.PM25: {"low": 15, "medium": 35, "high": 55, "critical": 150},
            PollutantType.PM10: {"low": 25, "medium": 50, "high": 90, "critical": 250},
            PollutantType.NO2: {"low": 40, "medium": 100, "high": 200, "critical": 400},
            PollutantType.O3: {"low": 60, "medium": 120, "high": 180, "critical": 240},
        }
        
        self.explanation_templates = {
            SeverityLevel.LOW: "Slightly elevated {pollutant} levels detected in {location}. This is a minor increase above normal baseline.",
            SeverityLevel.MEDIUM: "Moderate {pollutant} pollution spike detected in {location}. Levels are {deviation}% above normal baseline.",
            SeverityLevel.HIGH: "Significant {pollutant} pollution event in {location}. Current levels are {deviation}% higher than typical conditions.",
            SeverityLevel.CRITICAL: "CRITICAL pollution alert for {pollutant} in {location}. Extremely dangerous levels detected - {deviation}% above baseline."
        }
        
        self.action_recommendations = {
            SeverityLevel.LOW: [
                "Continue monitoring conditions",
                "Check for local emission sources",
                "Review weather patterns"
            ],
            SeverityLevel.MEDIUM: [
                "Issue public health advisory",
                "Recommend limiting outdoor activities for sensitive groups",
                "Investigate potential pollution sources",
                "Increase monitoring frequency"
            ],
            SeverityLevel.HIGH: [
                "Issue air quality warning to public",
                "Advise vulnerable populations to stay indoors",
                "Contact local environmental authorities",
                "Activate emergency response protocols",
                "Investigate industrial/traffic sources"
            ],
            SeverityLevel.CRITICAL: [
                "IMMEDIATE public health emergency alert",
                "Advise all residents to stay indoors",
                "Contact emergency services and health authorities",
                "Investigate and shut down pollution sources if possible",
                "Prepare for potential evacuations"
            ]
        }

    def process_anomaly(self, anomaly: AnomalyInput) -> AlertDecision:
        """
        Main decision logic - processes anomaly and decides if/how to alert
        """
        logger.info(f"Processing anomaly: {anomaly.pollutant.value} in {anomaly.location}")
        
        # Step 1: Determine if we should alert
        should_alert = self._should_create_alert(anomaly)
        
        if not should_alert:
            return AlertDecision(
                should_alert=False,
                severity=SeverityLevel.LOW,
                explanation=f"Minor fluctuation in {anomaly.pollutant.value} levels - within normal variation range.",
                recommended_actions=["Continue routine monitoring"],
                confidence=anomaly.confidence_score,
                reasoning="Deviation below alert threshold"
            )
        
        # Step 2: Determine severity level
        severity = self._calculate_severity(anomaly)
        
        # Step 3: Generate explanation
        explanation = self._generate_explanation(anomaly, severity)
        
        # Step 4: Get recommended actions
        actions = self._get_recommended_actions(severity, anomaly)
        
        # Step 5: Calculate overall confidence
        confidence = self._calculate_confidence(anomaly, severity)
        
        # Step 6: Generate reasoning
        reasoning = self._generate_reasoning(anomaly, severity)
        
        return AlertDecision(
            should_alert=True,
            severity=severity,
            explanation=explanation,
            recommended_actions=actions,
            confidence=confidence,
            reasoning=reasoning
        )

    def _should_create_alert(self, anomaly: AnomalyInput) -> bool:
        """Decide if anomaly warrants an alert"""
        # Basic thresholds for alerting
        min_deviation = 20  # 20% above baseline
        min_confidence = 0.6
        
        # Don't alert if confidence is too low
        if anomaly.confidence_score < min_confidence:
            return False
            
        # Don't alert for small deviations
        if abs(anomaly.deviation_percentage) < min_deviation:
            return False
            
        # Alert for significant positive deviations (pollution increases)
        if anomaly.deviation_percentage > min_deviation:
            return True
            
        return False

    def _calculate_severity(self, anomaly: AnomalyInput) -> SeverityLevel:
        """Calculate severity level based on pollutant value and deviation"""
        current_value = anomaly.current_value
        deviation = abs(anomaly.deviation_percentage)
        
        # Get thresholds for this pollutant
        thresholds = self.severity_thresholds.get(anomaly.pollutant, {})
        
        # Determine severity based on absolute value
        if current_value >= thresholds.get("critical", float('inf')):
            return SeverityLevel.CRITICAL
        elif current_value >= thresholds.get("high", float('inf')):
            return SeverityLevel.HIGH
        elif current_value >= thresholds.get("medium", float('inf')):
            return SeverityLevel.MEDIUM
        
        # Also consider deviation percentage
        if deviation > 200:  # 200% above baseline
            return SeverityLevel.CRITICAL
        elif deviation > 100:  # 100% above baseline
            return SeverityLevel.HIGH
        elif deviation > 50:   # 50% above baseline
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW

    def _generate_explanation(self, anomaly: AnomalyInput, severity: SeverityLevel) -> str:
        """Generate human-readable explanation"""
        template = self.explanation_templates[severity]
        
        return template.format(
            pollutant=anomaly.pollutant.value.upper(),
            location=anomaly.location,
            deviation=int(abs(anomaly.deviation_percentage))
        )

    def _get_recommended_actions(self, severity: SeverityLevel, anomaly: AnomalyInput) -> List[str]:
        """Get recommended actions based on severity"""
        base_actions = self.action_recommendations[severity].copy()
        
        # Add pollutant-specific actions
        if anomaly.pollutant == PollutantType.PM25 and severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            base_actions.append("Check for wildfire activity or dust storms")
            
        return base_actions

    def _calculate_confidence(self, anomaly: AnomalyInput, severity: SeverityLevel) -> float:
        """Calculate overall confidence in the alert decision"""
        base_confidence = anomaly.confidence_score
        
        # Adjust based on severity (higher severity = more confident if detected)
        severity_multiplier = {
            SeverityLevel.LOW: 0.9,
            SeverityLevel.MEDIUM: 1.0,
            SeverityLevel.HIGH: 1.1,
            SeverityLevel.CRITICAL: 1.2
        }
        
        adjusted_confidence = min(1.0, base_confidence * severity_multiplier[severity])
        return round(adjusted_confidence, 2)

    def _generate_reasoning(self, anomaly: AnomalyInput, severity: SeverityLevel) -> str:
        """Generate reasoning for the decision"""
        return f"""
        Decision based on:
        - Current {anomaly.pollutant.value.upper()}: {anomaly.current_value} μg/m³
        - Baseline: {anomaly.baseline_value} μg/m³  
        - Deviation: {anomaly.deviation_percentage:+.1f}%
        - Detection confidence: {anomaly.confidence_score:.2f}
        - Severity classification: {severity.value.upper()}
        """

# Demo/Testing Functions
def create_sample_anomaly() -> AnomalyInput:
    """Create sample anomaly data for testing"""
    return AnomalyInput(
        timestamp=datetime.now(),
        location="Downtown Los Angeles",
        pollutant=PollutantType.PM25,
        current_value=65.0,
        baseline_value=25.0,
        deviation_percentage=160.0,
        confidence_score=0.85,
        raw_data={"sensor_id": "LA_001", "weather": "calm"}
    )

def demo_agent():
    """Demo the AI agent with sample data"""
    print("🤖 Environmental AI Agent Demo")
    print("=" * 50)
    
    agent = EnvironmentalAIAgent()
    
    # Test with sample anomaly
    anomaly = create_sample_anomaly()
    decision = agent.process_anomaly(anomaly)
    
    print(f"📍 Location: {anomaly.location}")
    print(f"🏭 Pollutant: {anomaly.pollutant.value.upper()}")
    print(f"📊 Current Value: {anomaly.current_value} μg/m³")
    print(f"📈 Deviation: {anomaly.deviation_percentage:+.1f}%")
    print()
    print(f"🚨 Alert Decision: {'YES' if decision.should_alert else 'NO'}")
    print(f"⚠️  Severity: {decision.severity.value.upper()}")
    print(f"🎯 Confidence: {decision.confidence:.2f}")
    print()
    print(f"💬 Explanation:")
    print(f"   {decision.explanation}")
    print()
    print(f"📋 Recommended Actions:")
    for i, action in enumerate(decision.recommended_actions, 1):
        print(f"   {i}. {action}")
    print()
    print(f"🧠 Reasoning:{decision.reasoning}")

if __name__ == "__main__":
    demo_agent()