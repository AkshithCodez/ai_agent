"""
Quick test for NORMAL condition AI output
"""
import sys
sys.path.insert(0, 'c:\\Users\\reddy\\Downloads\\Hackathon\\Agentathon\\ai_agent\\WarningSystem')

from src.ai_adapter import get_ai_explanation

# Test with NORMAL status (low pollution)
test_result = {
    "status": "NORMAL",
    "severity_score": 0,
    "z_score": -1.48,
    "explanation": "Value is 1.48 standard deviations below normal",
    "baseline_mean": 272.91,
    "baseline_std": 183.07
}

print("="*70)
print("AI OUTPUT FOR NORMAL CONDITIONS")
print("="*70)

ai_output = get_ai_explanation(
    analysis_result=test_result,
    current_value=1.82,
    timestamp="2025-12-20 16:01:00 IST",
    location="Delhi",
    pollutant="pm25"
)

print("\n" + ai_output)
print("\n" + "="*70)
