"""
Comprehensive AI Advisory Generator
Provides rich, actionable intelligence for air quality monitoring.
"""

from typing import Dict
import os


def generate_comprehensive_advisory(sensor_data: Dict, satellite_data: Dict = None) -> str:
    """
    Generates a comprehensive advisory with situation summary, environmental context,
    health implications, and actions.
    
    Args:
        sensor_data: Dictionary containing:
            - current_value: PM2.5 value (µg/m³)
            - status: Alert status (NORMAL/WARNING/DISTRESS/CRITICAL)
            - z_score: Statistical deviation
            - baseline_mean: Historical average
            - baseline_std: Standard deviation
        satellite_data: Optional dictionary containing:
            - no2: NO2 index data
            - aerosol: Aerosol Index data
            - satellite: Satellite name
    
    Returns:
        Formatted advisory string with multiple sections
    """
    
    current_value = sensor_data.get("current_value", 0)
    status = sensor_data.get("status", "NORMAL")
    z_score = sensor_data.get("z_score", 0)
    baseline_mean = sensor_data.get("baseline_mean", 0)
    
    # Determine AQI category
    if current_value <= 12:
        aqi_category = "Good"
        color_emoji = "🟢"
    elif current_value <= 35.4:
        aqi_category = "Moderate"
        color_emoji = "🟡"
    elif current_value <= 55.4:
        aqi_category = "Unhealthy for Sensitive Groups"
        color_emoji = "🟠"
    elif current_value <= 150.4:
        aqi_category = "Unhealthy"
        color_emoji = "🔴"
    elif current_value <= 250.4:
        aqi_category = "Very Unhealthy"
        color_emoji = "🟣"
    else:
        aqi_category = "Hazardous"
        color_emoji = "🟤"
    
    # Build the advisory
    advisory_parts = []
    
    # Section 1: SITUATION SUMMARY
    advisory_parts.append("🛑 SITUATION SUMMARY")
    advisory_parts.append("-" * 50)
    
    if status == "CRITICAL":
        advisory_parts.append(f"⚠️ CRITICAL AIR QUALITY EMERGENCY")
        advisory_parts.append(f"PM2.5 levels have reached {current_value:.1f} µg/m³, which is")
        advisory_parts.append(f"{abs(z_score):.1f} standard deviations {'above' if z_score > 0 else 'below'} normal levels.")
        advisory_parts.append(f"This represents EXTREMELY DANGEROUS air quality.")
    elif status in ["WARNING", "DISTRESS"]:
        advisory_parts.append(f"⚠️ ELEVATED POLLUTION ALERT")
        advisory_parts.append(f"PM2.5 concentration is {current_value:.1f} µg/m³.")
        advisory_parts.append(f"This is {abs(z_score):.1f}x the normal variation from baseline.")
        advisory_parts.append(f"Air quality has deteriorated significantly.")
    else:
        advisory_parts.append(f"✅ NORMAL AIR QUALITY")
        advisory_parts.append(f"PM2.5 levels are {current_value:.1f} µg/m³.")
        advisory_parts.append(f"Conditions are within expected parameters.")
    
    advisory_parts.append(f"\n{color_emoji} AQI Category: {aqi_category}")
    advisory_parts.append(f"📊 Baseline Average: {baseline_mean:.1f} µg/m³")
    
    # Section 2: ENVIRONMENTAL CONTEXT (Air Quality Satellite Data)
    # ONLY show if we have actual pollution data
    if satellite_data and isinstance(satellite_data, dict):
        data_source = satellite_data.get("data_source", "Unknown")
        
        if data_source not in ["Unavailable", "Simulated (Fallback)"]:
            advisory_parts.append(f"\n\n🛰️ ENVIRONMENTAL CONTEXT - AIR QUALITY")
            advisory_parts.append("-" * 50)
        
        no2_data = satellite_data.get('no2', {})
        aerosol_data = satellite_data.get('aerosol', {})
        
        no2_value = no2_data.get('value')
        no2_status = no2_data.get('status', 'UNKNOWN')
        aerosol_value = aerosol_data.get('value')
        aerosol_status = aerosol_data.get('status', 'UNKNOWN')
        
        if no2_value is not None:
            advisory_parts.append(f"🚗 NO2 (Traffic/Industrial Emissions): {no2_value:.3f} - {no2_status.replace('_', ' ')}")
        else:
            advisory_parts.append(f"🚗 NO2 (Traffic/Industrial Emissions): Data Unavailable")
            
        if aerosol_value is not None:
            advisory_parts.append(f"💨 Aerosol Index: {aerosol_value:.2f} - {aerosol_status.replace('_', ' ')}")
        else:
            advisory_parts.append(f"💨 Aerosol Index: Data Unavailable")
        
        # Correlate air quality metrics - ONLY discuss negative impacts if pollution is elevated
        if no2_value is not None or aerosol_value is not None:
            advisory_parts.append("\n🔗 Environmental Correlations:")
            
            # NO2 correlation - traffic/industrial emissions
            if no2_value is not None:
                if no2_value > 0.2:
                    advisory_parts.append("• High NO2 indicates significant industrial emissions or heavy traffic")
                    advisory_parts.append("  - Pollution sources likely include nearby industrial zones")
                    advisory_parts.append("  - Consider traffic diversion routes during peak hours")
                elif no2_value > 0.1:
                    advisory_parts.append("• Moderate NO2 levels suggest mixed traffic and light industrial activity")
                else:
                    advisory_parts.append("• Low NO2 indicates minimal traffic and industrial influence")
            
            # Aerosol correlation - particulate matter
            if aerosol_value is not None:
                if aerosol_value > 2.0:
                    advisory_parts.append("• High aerosol index confirms significant particulate pollution")
                elif aerosol_value > 1.0:
                    advisory_parts.append("• Moderate aerosol levels indicate some airborne particles present")
                elif aerosol_value > 0.0:
                    advisory_parts.append("• Light aerosol presence - generally acceptable conditions")
                else:
                    advisory_parts.append("• Clear atmospheric conditions with minimal particulates")
        
        advisory_parts.append(f"\n📡 Data Source: {satellite_data.get('satellite', 'Unknown')}")
    
    # Section 3: HEALTH IMPLICATIONS
    advisory_parts.append(f"\n\n🩺 HEALTH IMPLICATIONS")
    advisory_parts.append("-" * 50)
    
    if current_value > 150:
        advisory_parts.append("❗ SEVERE HEALTH RISK")
        advisory_parts.append("• Everyone: Serious health effects likely")
        advisory_parts.append("• Respiratory symptoms (coughing, shortness of breath)")
        advisory_parts.append("• Cardiovascular stress (heart palpitations)")
        advisory_parts.append("• Children & elderly at EXTREME risk")
        advisory_parts.append("• Asthmatics: Emergency medication may be needed")
    elif current_value > 55:
        advisory_parts.append("⚠️ MODERATE TO HIGH HEALTH RISK")
        advisory_parts.append("• Sensitive groups: Significant health effects")
        advisory_parts.append("• General public: Respiratory irritation possible")
        advisory_parts.append("• Children, elderly, and those with lung/heart disease")
        advisory_parts.append("  should take precautions")
    elif current_value > 35:
        advisory_parts.append("⚠️ SENSITIVE GROUPS AT RISK")
        advisory_parts.append("• People with asthma may experience symptoms")
        advisory_parts.append("• Children and elderly should limit prolonged exertion")
        advisory_parts.append("• General public: Minimal risk")
    elif current_value > 12:
        advisory_parts.append("ℹ️ ACCEPTABLE QUALITY")
        advisory_parts.append("• Unusually sensitive individuals may experience")
        advisory_parts.append("  minor respiratory symptoms")
        advisory_parts.append("• General public: No health impacts expected")
    else:
        advisory_parts.append("✅ EXCELLENT AIR QUALITY")
        advisory_parts.append("• No health impacts expected for any group")
        advisory_parts.append("• Ideal conditions for outdoor activities")
    
    # Section 4: IMMEDIATE ACTIONS
    advisory_parts.append(f"\n\n🛡️ IMMEDIATE ACTIONS")
    advisory_parts.append("-" * 50)
    
    if current_value > 150:
        advisory_parts.append("🚨 EMERGENCY PROTOCOL:")
        advisory_parts.append("1. Stay indoors with windows/doors closed")
        advisory_parts.append("2. Use air purifiers with HEPA filters")
        advisory_parts.append("3. Wear N95/N99 masks if you must go outside")
        advisory_parts.append("4. Cancel all outdoor activities and events")
        advisory_parts.append("5. Monitor health - seek medical help if symptoms worsen")
        advisory_parts.append("6. Keep emergency medications accessible")
        advisory_parts.append("7. Check on vulnerable neighbors/family")
    elif current_value > 55:
        advisory_parts.append("⚠️ PROTECTIVE MEASURES:")
        advisory_parts.append("1. Limit outdoor exposure, especially for sensitive groups")
        advisory_parts.append("2. Wear KN95 masks during outdoor activities")
        advisory_parts.append("3. Avoid strenuous outdoor exercise")
        advisory_parts.append("4. Keep windows closed during peak pollution hours")
        advisory_parts.append("5. Use air purifiers indoors if available")
        advisory_parts.append("6. Asthmatics: Keep rescue inhalers handy")
    elif current_value > 35:
        advisory_parts.append("ℹ️ PRECAUTIONARY STEPS:")
        advisory_parts.append("1. Sensitive groups: Reduce prolonged outdoor exertion")
        advisory_parts.append("2. Consider wearing masks during extended outdoor time")
        advisory_parts.append("3. Monitor air quality before outdoor activities")
        advisory_parts.append("4. Children: Limit intense outdoor sports")
    elif current_value > 12:
        advisory_parts.append("✅ STANDARD PRECAUTIONS:")
        advisory_parts.append("1. Unusually sensitive people: Watch for symptoms")
        advisory_parts.append("2. General public: Normal outdoor activities OK")
        advisory_parts.append("3. Continue routine air quality monitoring")
    else:
        advisory_parts.append("✅ NO SPECIAL ACTIONS NEEDED:")
        advisory_parts.append("1. Enjoy outdoor activities freely")
        advisory_parts.append("2. Excellent conditions for exercise and recreation")
        advisory_parts.append("3. Continue routine monitoring")
    
    return "\n".join(advisory_parts)


def generate_fallback_advisory(status: str) -> str:
    """Fallback advisory when AI service is unavailable"""
    
    fallback_messages = {
        "CRITICAL": """🛑 CRITICAL POLLUTION ALERT
AI service unavailable, but sensor data indicates DANGEROUS levels.
🩺 HEALTH: Severe risk to all groups
🛡️ ACTION: Stay indoors, wear N95 masks, seek medical help if needed""",
        
        "DISTRESS": """⚠️ HIGH POLLUTION ALERT
AI service unavailable, but sensor data indicates ELEVATED levels.
🩺 HEALTH: Moderate to high risk
🛡️ ACTION: Limit outdoor exposure, wear masks, avoid strenuous activity""",
        
        "WARNING": """⚠️ POLLUTION WARNING
AI service unavailable, but sensor data indicates ABOVE NORMAL levels.
🩺 HEALTH: Sensitive groups at risk
🛡️ ACTION: Reduce outdoor exertion, monitor symptoms""",
        
        "NORMAL": """✅ NORMAL CONDITIONS
AI service unavailable, but sensor data indicates NORMAL levels.
🩺 HEALTH: No significant health impacts
🛡️ ACTION: Continue routine monitoring"""
    }
    
    return fallback_messages.get(status, "AI service unavailable. Manual review recommended.")