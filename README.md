# Early Warning Intelligence Layer 🚨

## Real-Time Environmental Monitoring System with Statistical Anomaly Detection

Early Warning Intelligence Layer is a production-ready environmental monitoring system designed to continuously analyze air quality data and detect pollution anomalies using statistical intelligence.

The system performs real-time PM2.5 monitoring using Z-Score based anomaly detection, enabling explainable and lightweight environmental risk analysis without requiring complex machine learning model training.

Built during Agentathon 2025, the project focuses on reliability, automation, explainability, and seamless dashboard integration.

---

# Features

- Real-time PM2.5 environmental monitoring
- Statistical anomaly detection using Z-Score analysis
- Continuous background monitoring service
- Automated severity classification system
- Secure environment variable-based API key management
- JSON export for dashboard integration
- Graceful API failure handling with intelligent fallback logic
- Lightweight and explainable analytical pipeline

---

# System Architecture

## Monitoring Workflow

1. Fetch historical PM2.5 measurements
2. Establish baseline environmental statistics
3. Retrieve latest live air quality measurement
4. Calculate anomaly score using Z-Score analysis
5. Classify pollution severity level
6. Export structured alert data to JSON
7. Repeat monitoring every 5 minutes

---

# Tech Stack

## Backend
- Python

## Libraries
- NumPy
- Pandas
- Requests

## Infrastructure
- OpenAQ API
- JSON-based dashboard integration

---

# Alert Classification System

| Status | Z-Score Range | Severity |
|--------|---------------|----------|
| NORMAL | \|Z\| < 1.5 | 0/3 |
| WARNING | 1.5 ≤ \|Z\| < 2.0 | 1/3 |
| DISTRESS | 2.0 ≤ \|Z\| < 3.0 | 2/3 |
| CRITICAL | \|Z\| ≥ 3.0 | 3/3 |

---

# Quick Start

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Environment Variables

```bash
cp .env.example .env
```

Add your API key inside the `.env` file:

```env
OPENAQ_API_KEY=your_api_key_here
```

> The system can also operate using realistic simulated environmental data for demonstration purposes.

---

## 3. Run the Monitoring Service

```bash
python main.py
```

The monitoring service will continuously run in the background and analyze environmental data every 5 minutes.

Press `Ctrl + C` to stop the service gracefully.

---

# Dashboard Integration

The system exports monitoring results to:

```bash
data/latest_alert.json
```

This enables easy integration with external dashboards and visualization systems.

## Example JSON Output

```json
{
  "timestamp": "2025-12-20T13:24:47.742489",
  "status": "NORMAL",
  "severity_score": 0,
  "z_score": 0.04,
  "explanation": "Value is 0.04 standard deviations above normal.",
  "current_value": 161.04,
  "baseline_mean": 159.33,
  "baseline_std": 46.18,
  "city": "Delhi",
  "parameter": "pm25"
}
```

---

# Example Diagnostic Output

```text
======================================================================

  DIAGNOSTIC REPORT

======================================================================

STATUS: DISTRESS
Severity Score: 2/3

MEASUREMENTS:
  Current Value: 256.29 µg/m³
  Timestamp: 2025-12-20T13:00:00.307592

BASELINE STATISTICS:
  Mean: 160.92 µg/m³
  Std Dev: 46.86 µg/m³

ANOMALY DETECTION:
  Z-Score: 2.04

EXPLANATION:
  Value is 2.04 standard deviations above normal.

======================================================================
```

---

# Project Structure

```text
WarningSystem/
├── src/
│   ├── config.py
│   ├── ingestion.py
│   └── analysis.py
├── data/
│   └── latest_alert.json
├── main.py
├── requirements.txt
└── .env.example
```

---

# Configuration

Modify monitoring settings inside:

```bash
src/config.py
```

Example configuration:

```python
TARGET_CITY = "Delhi"
PARAMETER = "pm25"

THRESHOLDS = {
    "LOW_WARNING": 1.5,
    "MEDIUM_DISTRESS": 2.0,
    "HIGH_CRITICAL": 3.0
}
```

---

# Data Source

## Primary Source
- OpenAQ API v3

## Fallback Source
- Simulated environmental data modeled on realistic Delhi PM2.5 patterns

---

# Future Improvements

- Multi-city monitoring support
- Historical trend visualization
- Real-time web dashboard
- Email and SMS alert systems
- Cloud deployment support
- Advanced anomaly detection techniques
- Time-series forecasting integration

---

# License

This project was developed for hackathon and educational purposes.

---

# Author

Developed as part of Agentathon 2025 to explore real-time environmental intelligence systems using lightweight statistical AI techniques.
