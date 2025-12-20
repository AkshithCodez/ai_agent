"""Test AI engine output"""
import sys
sys.path.insert(0, 'c:\\Users\\reddy\\Downloads\\Hackathon\\Agentathon\\ai_agent\\WarningSystem')

from src.ai_engine import generate_comprehensive_advisory

sensor_data = {
    "current_value": 1.82,
    "status": "NORMAL",
    "z_score": -1.47,
    "baseline_mean": 270.53,
    "baseline_std": 183.19
}

print("Testing AI Engine...")
print("="*70)

try:
    result = generate_comprehensive_advisory(sensor_data)
    print("SUCCESS!")
    print("\nOutput:")
    print(result)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
