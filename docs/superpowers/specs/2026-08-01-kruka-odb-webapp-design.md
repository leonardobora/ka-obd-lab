# Kruka OBD Project — Web App Design

## Overview

A web-based dashboard for real-time OBD-II telemetry from a Ford Ka 2017 (KRU) via an ELM327 Bluetooth/WiFi scanner. The app uses FastAPI for the backend and vanilla HTML/CSS/JS for the frontend, with Plotly.js for charts and custom SVG gauges.

## Architecture

```
FastAPI backend (Python)
├── /ws          ← WebSocket endpoint for live OBD data
├── /connect     ← POST to initiate Bluetooth/WiFi connection
├── /pids        ← GET available PIDs and metadata
├── /            ← Serves the HTML/CSS/JS frontend
└── obd_client.py ← existing client (reused as-is)

Frontend (vanilla HTML/CSS/JS, served as static files)
├── index.html   ← main dashboard
├── style.css    ← dark theme, gauge styles, layout
└── app.js       ← WebSocket client, Plotly charts, UI logic
```

## Screens

### Main Dashboard

- **Top bar**: "Kruka OBD Project" title, connection status indicator (green dot = connected, red = disconnected), Connect/Retry button, Bluetooth COM port selector
- **Gauges row**: RPM (large circular gauge), Speed (circular), Coolant Temp (circular)
- **Cards row**: Throttle Position, Engine Load, Intake Air Temp, MAF, Fuel Level, Battery Voltage — numeric values in dark cards
- **Bottom**: Plotly chart with multiple traces (RPM, speed, coolant, throttle) — toggleable via legend

### Data Flow

1. User opens the app → auto-connects to configured scanner
2. FastAPI WebSocket pushes OBD readings every 500ms
3. Frontend updates gauges, cards, and Plotly chart in real-time
4. If connection drops → UI shows "Disconnected" + Retry button
5. User clicks Retry → reconnection attempt

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Charts**: Plotly.js (CDN)
- **WebSocket**: FastAPI WebSocket endpoint
- **OBD Client**: Existing `obd_client.py` (reused)
- **Hosting**: Hugging Face Spaces (primary), Vercel (alternative)

## Key Design Decisions

- Dark theme throughout (fits garage/hacker vibe)
- Both circular gauges (for RPM, speed, coolant) and numeric cards (for remaining PIDs)
- Single Plotly chart with multiple traces, toggleable via legend
- Auto-connect on page load with manual retry button
- WebSocket for real-time updates (not polling)
- No frontend framework — keeps the project simple and maintainable

## Deployment

### Hugging Face Spaces (primary)
- Create a Spaces app with Python SDK
- New `main.py` entry point: FastAPI app with WebSocket + static file serving
- Update `requirements.txt` to include FastAPI, uvicorn, pyserial, websockets
- Static files served from `/static` directory

### Vercel (alternative)
- FastAPI can be deployed via Vercel's Python support
- Requires `vercel.json` configuration
- Slightly more setup than HF Spaces

## Configuration

- The scanner connection (COM port for Bluetooth, IP:port for WiFi) is configurable via the UI settings panel
- Defaults: COM5 for Bluetooth, `192.168.0.10:35000` for WiFi

## Next Steps (post-MVP)

- Read DTCs (mode 03) and VIN (mode 09)
- CSV logging with timestamps
- Tier 2: FORScan / Ford module access
- Tier 3: Raw CAN bus sniffing