# Early Warning Intelligence Layer 🚨

**Real-time Environmental Monitoring System with Statistical Anomaly Detection**

A production-ready Python background service that continuously monitors air quality (PM2.5) and detects pollution anomalies using Z-Score statistical analysis. Now featuring secure API key management, JSON export for dashboard integration, and automated continuous monitoring.

## 🆕 Latest Upgrades

- 🔒 **Secure API Key Management** - Environment variable-based configuration
- 📊 **Dashboard Integration** - JSON export to `data/latest_alert.json`
- 🔄 **Background Service** - Continuous monitoring with 5-minute intervals
- 🛡️ **Robust Error Handling** - Automatic recovery from failures

## Features

✅ **Simple** - No complex ML training, pure statistical logic  
✅ **Robust** - Graceful API failure handling with intelligent fallback  
✅ **Explainable** - Clear Z-Score calculations and severity levels  
✅ **Secure** - API credentials managed via environment variables  
✅ **Automated** - Runs continuously as a background service  
✅ **Integrated** - Exports JSON for dashboard consumption  

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAQ API key
# OPENAQ_API_KEY=your_actual_key_here
```

> **Note**: The system works without an API key using realistic simulated data for demo purposes.

### 3. Run Background Service
```bash
python main.py
```

The service will run continuously, monitoring air quality every 5 minutes. Press `Ctrl+C` to stop gracefully.

## How It Works

1. **Baseline Establishment**: Fetches 100 historical PM2.5 measurements
2. **Live Monitoring**: Gets the most recent air quality reading
3. **Anomaly Detection**: Calculates Z-Score to detect deviations
4. **Alert Generation**: Classifies severity and displays diagnostic report
5. **JSON Export**: Saves results to `data/latest_alert.json` for dashboard integration
6. **Continuous Loop**: Repeats every 5 minutes automatically

## Dashboard Integration

The service exports analysis results to `data/latest_alert.json` for easy integration with dashboards:

```json
{
  "timestamp": "2025-12-20T13:24:47.742489",
  "status": "NORMAL",
  "severity_score": 0,
  "z_score": 0.04,
  "explanation": "Value is 0.04 standard deviations above normal...",
  "current_value": 161.04,
  "baseline_mean": 159.33,
  "baseline_std": 46.18,
  "city": "Delhi",
  "parameter": "pm25"
}
```

**For Dashboard Developers**: Poll this file every 30-60 seconds to display real-time alerts.

## Alert Levels

| Status | Z-Score Range | Severity |
|--------|---------------|----------|
| ✓ NORMAL | \|Z\| < 1.5 | 0/3 |
| ⚠ WARNING | 1.5 ≤ \|Z\| < 2.0 | 1/3 |
| ⚠⚠ DISTRESS | 2.0 ≤ \|Z\| < 3.0 | 2/3 |
| 🚨 CRITICAL | \|Z\| ≥ 3.0 | 3/3 |

## Example Output

```
======================================================================
  DIAGNOSTIC REPORT
======================================================================

⚠⚠ STATUS: DISTRESS
  Severity Score: 2/3

📊 MEASUREMENTS:
  Current Value: 256.29 µg/m³
  Timestamp: 2025-12-20T13:00:00.307592

📈 BASELINE STATISTICS:
  Mean: 160.92 µg/m³
  Std Dev: 46.86 µg/m³

🔬 ANOMALY DETECTION:
  Z-Score: 2.04
  Thresholds:
    - Warning: ±1.5
    - Distress: ±2.0
    - Critical: ±3.0

💡 EXPLANATION:
  Value is 2.04 standard deviations above normal.
======================================================================
```

## Project Structure

```
WarningSystem/
├── src/
│   ├── config.py       # Configuration & thresholds
│   ├── ingestion.py    # Data fetching & simulation
│   └── analysis.py     # Z-Score anomaly detection
├── main.py             # Main execution pipeline
└── requirements.txt    # Dependencies
```

## Configuration

Edit `src/config.py` to customize:

```python
TARGET_CITY = "Delhi"
PARAMETER = "pm25"

THRESHOLDS = {
    "LOW_WARNING": 1.5,
    "MEDIUM_DISTRESS": 2.0,
    "HIGH_CRITICAL": 3.0
}
```

## Dependencies

- `requests` - API communication
- `pandas` - Data manipulation
- `numpy` - Statistical calculations

## Data Source

- **Primary**: OpenAQ API v3 (requires authentication)
- **Fallback**: Intelligent simulated data based on Delhi's typical PM2.5 patterns

## Future Enhancements

- 🔐 API authentication for real-time data
- 🌍 Multi-city monitoring
- 📊 Historical trend analysis
- 📧 Email/SMS alert notifications
- 🌐 Web dashboard with real-time visualization

## License

Built for hackathon demonstration purposes.

---

**Made with ❤️ for environmental monitoring**
