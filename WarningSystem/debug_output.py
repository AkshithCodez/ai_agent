"""
Debug script to test AI output formatting
"""
import sys
sys.path.insert(0, 'c:\\Users\\reddy\\Downloads\\Hackathon\\Agentathon\\ai_agent\\WarningSystem')

from src.ai_adapter import get_ai_explanation

# Test with WARNING status
print("="*70)
print("Testing AI Output - Full Debug")
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
    print("\n[DEBUG] Calling get_ai_explanation...")
    ai_explanation = get_ai_explanation(
        analysis_result=test_result,
        current_value=150.0,
        timestamp="2025-12-20 17:00:00 IST",
        location="Delhi",
        pollutant="pm25"
    )
    
    print("\n[DEBUG] AI Explanation returned successfully")
    print(f"[DEBUG] Type: {type(ai_explanation)}")
    print(f"[DEBUG] Length: {len(ai_explanation)} characters")
    print("\n" + "="*70)
    print("AI ADVISORY")
    print("="*70)
    print(f"\n{ai_explanation}\n")
    print("="*70)
    
    # Also print character by character to see if there are hidden characters
    print("\n[DEBUG] First 200 characters:")
    print(repr(ai_explanation[:200]))
    
except Exception as e:
    print(f"\n❌ Test FAILED: {e}")
    import traceback
    traceback.print_exc()
