"""
Quick Verification Script - Run this to see AI output working correctly
Save output to file to view complete results
"""
import sys
sys.path.insert(0, 'c:\\Users\\reddy\\Downloads\\Hackathon\\Agentathon\\ai_agent\\WarningSystem')

from src.ai_adapter import get_ai_explanation

def test_ai_output():
    """Test AI output generation with different scenarios"""
    
    scenarios = [
        {
            "name": "WARNING - Moderate Pollution",
            "result": {
                "status": "WARNING",
                "severity_score": 1,
                "z_score": 1.8,
                "explanation": "Value is 1.8 standard deviations above normal",
                "baseline_mean": 50.0,
                "baseline_std": 30.0
            },
            "current_value": 104.0
        },
        {
            "name": "CRITICAL - Severe Pollution",
            "result": {
                "status": "CRITICAL",
                "severity_score": 3,
                "z_score": 4.5,
                "explanation": "Value is 4.5 standard deviations above normal",
                "baseline_mean": 40.0,
                "baseline_std": 25.0
            },
            "current_value": 200.0
        }
    ]
    
    for scenario in scenarios:
        print("\n" + "="*70, flush=True)
        print(f"  SCENARIO: {scenario['name']}", flush=True)
        print("="*70, flush=True)
        sys.stdout.flush()
        
        try:
            ai_explanation = get_ai_explanation(
                analysis_result=scenario['result'],
                current_value=scenario['current_value'],
                timestamp="2025-12-20 17:00:00 IST",
                location="Delhi",
                pollutant="pm25"
            )
            
            print(f"\n{ai_explanation}\n", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70, flush=True)
    print("  VERIFICATION COMPLETE", flush=True)
    print("="*70, flush=True)
    print("\n✅ If you can see the AI explanations and recommended actions above,")
    print("   the system is working correctly!", flush=True)
    print("\n💡 TIP: Run this script directly in PowerShell to see full output:")
    print("   python verify_ai_output.py", flush=True)

if __name__ == "__main__":
    test_ai_output()
