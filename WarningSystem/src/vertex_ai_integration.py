"""
Vertex AI / Gemini Integration for Enhanced AI Agent
Member B - Advanced AI capabilities using Google's Gemini
"""

import os
import json
from typing import Dict, List, Optional
import google.generativeai as genai
from ai_agent import AnomalyInput, AlertDecision, SeverityLevel, EnvironmentalAIAgent

class GeminiEnhancedAgent(EnvironmentalAIAgent):
    """
    Enhanced AI Agent using Google's Gemini for more sophisticated reasoning
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        
        # Configure Gemini
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.gemini_available = True
        else:
            print("⚠️  Gemini API key not found. Using basic agent logic.")
            self.gemini_available = False

    def generate_enhanced_explanation(self, anomaly: AnomalyInput, decision: AlertDecision) -> str:
        """
        Use Gemini to generate more sophisticated explanations
        """
        if not self.gemini_available:
            return decision.explanation
            
        prompt = f"""
        You are an environmental health expert explaining a pollution alert to the public.
        
        Situation:
        - Location: {anomaly.location}
        - Pollutant: {anomaly.pollutant.value.upper()}
        - Current level: {anomaly.current_value} μg/m³
        - Normal baseline: {anomaly.baseline_value} μg/m³
        - Increase: {anomaly.deviation_percentage:.1f}% above normal
        - Severity: {decision.severity.value.upper()}
        
        Write a clear, non-technical explanation (2-3 sentences) that:
        1. Explains what's happening
        2. Why people should care
        3. What it means for health
        
        Keep it calm but informative. Avoid technical jargon.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return decision.explanation

    def analyze_pollution_context(self, anomaly: AnomalyInput) -> Dict[str, str]:
        """
        Use Gemini to provide contextual analysis of pollution event
        """
        if not self.gemini_available:
            return {"context": "Basic analysis - Gemini not available"}
            
        prompt = f"""
        Analyze this pollution event as an environmental expert:
        
        Event Details:
        - Pollutant: {anomaly.pollutant.value.upper()}
        - Location: {anomaly.location}
        - Current reading: {anomaly.current_value} μg/m³
        - Baseline: {anomaly.baseline_value} μg/m³
        - Time: {anomaly.timestamp.strftime('%Y-%m-%d %H:%M')}
        
        Provide brief analysis on:
        1. Likely sources of this pollutant in this area
        2. Weather factors that might contribute
        3. Health implications for different groups
        4. Expected duration/patterns
        
        Keep each point to 1-2 sentences. Be specific to the pollutant and location.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse response into structured format
            return {
                "context_analysis": response.text.strip(),
                "generated_by": "gemini-pro"
            }
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {"context": f"Analysis error: {e}"}

    def suggest_targeted_actions(self, anomaly: AnomalyInput, decision: AlertDecision) -> List[str]:
        """
        Use Gemini to suggest more targeted, location-specific actions
        """
        if not self.gemini_available:
            return decision.recommended_actions
            
        prompt = f"""
        As an emergency response coordinator, suggest specific actions for this pollution event:
        
        Situation:
        - {anomaly.pollutant.value.upper()} pollution in {anomaly.location}
        - Severity: {decision.severity.value.upper()}
        - Current level: {anomaly.current_value} μg/m³ ({anomaly.deviation_percentage:.1f}% above normal)
        
        Suggest 4-6 specific, actionable steps for:
        1. Immediate public protection
        2. Investigation/monitoring
        3. Source control
        4. Communication
        
        Make suggestions specific to this pollutant type and location. Be practical and prioritized.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse response into list
            actions = [line.strip() for line in response.text.split('\n') if line.strip() and not line.strip().startswith('#')]
            return actions[:6]  # Limit to 6 actions
        except Exception as e:
            print(f"Gemini API error: {e}")
            return decision.recommended_actions

    def process_anomaly_enhanced(self, anomaly: AnomalyInput) -> AlertDecision:
        """
        Enhanced anomaly processing with Gemini integration
        """
        # Get basic decision from parent class
        decision = super().process_anomaly(anomaly)
        
        if not decision.should_alert or not self.gemini_available:
            return decision
            
        # Enhance with Gemini
        enhanced_explanation = self.generate_enhanced_explanation(anomaly, decision)
        enhanced_actions = self.suggest_targeted_actions(anomaly, decision)
        context_analysis = self.analyze_pollution_context(anomaly)
        
        # Update decision with enhanced content
        decision.explanation = enhanced_explanation
        decision.recommended_actions = enhanced_actions
        
        # Add context to reasoning
        decision.reasoning += f"\n\nEnhanced Analysis:\n{context_analysis.get('context_analysis', '')}"
        
        return decision

# Setup and Configuration Functions
def setup_gemini_environment():
    """
    Setup instructions for Gemini API
    """
    print("🔧 Setting up Gemini AI Environment")
    print("=" * 40)
    print()
    print("1. Get Gemini API Key:")
    print("   - Go to: https://makersuite.google.com/app/apikey")
    print("   - Create new API key")
    print()
    print("2. Set Environment Variable:")
    print("   Windows: set GEMINI_API_KEY=your_api_key_here")
    print("   Linux/Mac: export GEMINI_API_KEY=your_api_key_here")
    print()
    print("3. Install Dependencies:")
    print("   pip install google-generativeai")
    print()
    print("4. Test Connection:")
    print("   python vertex_ai_integration.py")

def test_gemini_connection():
    """Test if Gemini is properly configured"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY environment variable not set")
            return False
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Simple test
        response = model.generate_content("Say 'Gemini connection successful'")
        print(f"✅ Gemini connected: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False

def demo_enhanced_agent():
    """Demo the enhanced agent with Gemini"""
    print("🚀 Enhanced AI Agent with Gemini Demo")
    print("=" * 50)
    
    # Test Gemini connection first
    if not test_gemini_connection():
        print("\n⚠️  Running with basic agent (no Gemini)")
    
    # Create enhanced agent
    agent = GeminiEnhancedAgent()
    
    # Create sample anomaly
    from ai_agent import create_sample_anomaly
    anomaly = create_sample_anomaly()
    
    # Process with enhanced logic
    decision = agent.process_anomaly_enhanced(anomaly)
    
    print(f"\n📍 Location: {anomaly.location}")
    print(f"🏭 Pollutant: {anomaly.pollutant.value.upper()}")
    print(f"📊 Current Value: {anomaly.current_value} μg/m³")
    print(f"📈 Deviation: {anomaly.deviation_percentage:+.1f}%")
    print()
    print(f"🚨 Alert Decision: {'YES' if decision.should_alert else 'NO'}")
    print(f"⚠️  Severity: {decision.severity.value.upper()}")
    print(f"🎯 Confidence: {decision.confidence:.2f}")
    print()
    print(f"💬 Enhanced Explanation:")
    print(f"   {decision.explanation}")
    print()
    print(f"📋 Enhanced Recommended Actions:")
    for i, action in enumerate(decision.recommended_actions, 1):
        print(f"   {i}. {action}")

if __name__ == "__main__":
    # Check if this is setup or demo
    if os.getenv('GEMINI_API_KEY'):
        demo_enhanced_agent()
    else:
        setup_gemini_environment()