"""
Test script to verify AI integration
"""
import sys
sys.path.insert(0, 'c:\\Users\\reddy\\Downloads\\Hackathon\\Agentathon\\ai_agent\\WarningSystem')

from src.ai_adapter import get_ai_explanation

# Test with WARNING status
print("="*70)
print("Testing AI Integration - WARNING Status")
print("="*70)

test_result = {
    "status": "WARNING",
    "severity_score": 1,
    "z_score": 1.8,
    "explanation": "Value is 1.8 standard deviations above normal",
    "baseline_mean": 50.0,
    "baseline_std": 30.0
}

try:
    ai_explanation = get_ai_explanation(
        analysis_result=test_result,
        current_value=150.0,
        timestamp="2025-12-20 17:00:00 IST",
        location="Delhi",
        pollutant="pm25"
    )
    
    print("\n✅ AI Integration Test PASSED")
    print("\nAI Explanation:")
    print(ai_explanation)
    
except Exception as e:
    print(f"\n❌ AI Integration Test FAILED: {e}")
    import traceback
    traceback.print_exc()
