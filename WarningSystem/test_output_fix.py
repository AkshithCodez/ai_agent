"""
Simple test to verify AI output is displayed correctly
"""
import sys
sys.path.insert(0, 'c:\\Users\\reddy\\Downloads\\Hackathon\\Agentathon\\ai_agent\\WarningSystem')

from src.ai_adapter import get_ai_explanation

print("="*70, flush=True)
print("AI Output Test - With Explicit Flushing", flush=True)
print("="*70, flush=True)
sys.stdout.flush()

test_result = {
    "status": "WARNING",
    "severity_score": 1,
    "z_score": 1.8,
    "explanation": "Value is 1.8 standard deviations above normal",
    "baseline_mean": 50.0,
    "baseline_std": 30.0
}

print("\n[TEST] Calling AI explanation function...", flush=True)
sys.stdout.flush()

ai_explanation = get_ai_explanation(
    analysis_result=test_result,
    current_value=150.0,
    timestamp="2025-12-20 17:00:00 IST",
    location="Delhi",
    pollutant="pm25"
)

print("\n" + "="*70, flush=True)
print("  AI ADVISORY", flush=True)
print("="*70, flush=True)
sys.stdout.flush()

print(f"\n{ai_explanation}\n", flush=True)
sys.stdout.flush()

print("="*70, flush=True)
sys.stdout.flush()

print("\n[TEST] ✅ Output test complete!", flush=True)
