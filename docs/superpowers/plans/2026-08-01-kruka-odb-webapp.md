# Kruka OBD Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real-time web dashboard for Kruka OBD telemetry with FastAPI backend, Plotly.js charts, and custom SVG gauges.

**Architecture:** FastAPI serves the API + WebSocket + static files. Frontend is vanilla HTML/CSS/JS. The existing `obd_client.py` is reused for OBD communication. WebSocket pushes readings every 500ms.

**Tech Stack:** FastAPI, uvicorn, pyserial, websockets, Plotly.js (CDN), vanilla JS

## Global Constraints

- Dark theme throughout
- Auto-connect on page load with manual retry button
- WebSocket for real-time updates (not polling)
- No frontend framework — vanilla HTML/CSS/JS only
- Hugging Face Spaces deployment target
- Scanner connection configurable via UI (COM port for BT, IP:port for WiFi)

---

## File Structure

```
ka-obd-lab/
├── main.py                    # NEW — FastAPI app entry point
├── requirements.txt           # MODIFY — add FastAPI, uvicorn, websockets
├── static/
│   ├── index.html             # NEW — dashboard HTML
│   ├── style.css              # NEW — dark theme styles
│   └── app.js                 # NEW — WebSocket client + Plotly + UI logic
├── obd_client.py              # EXISTING — reused as-is
├── mock_elm327.py             # EXISTING — reused as-is
├── pids.py                    # EXISTING — reused as-is
├── read_live.py               # EXISTING — reused as-is
└── README.md                  # MODIFY — add web app usage section
```

---

### Task 1: Update requirements.txt with web dependencies

**Files:**
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: existing `requirements.txt`
- Produces: updated `requirements.txt` with web deps

- [ ] **Step 1: Add FastAPI, uvicorn, and websockets to requirements.txt**

Append the following lines to `requirements.txt`:
```
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
```

- [ ] **Step 2: Install dependencies and verify**

Run: `pip install -r requirements.txt`
Expected: All packages install without errors

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "feat: add FastAPI, uvicorn, websockets to requirements"
```

---

### Task 2: Create FastAPI backend (main.py)

**Files:**
- Create: `main.py`

**Interfaces:**
- Consumes: `obd_client.py` (ELM327Client), `pids.py` (PIDS)
- Produces: FastAPI app with `/`, `/ws`, `/connect` endpoints

- [ ] **Step 1: Create main.py with FastAPI app, WebSocket endpoint, and static file serving**

Create `main.py` with:
- FastAPI app instance
- `GET /` — serves `static/index.html`
- `GET /ws` — WebSocket endpoint that accepts connections, runs OBD init, then pushes PID readings every 500ms
- `POST /connect` — accepts JSON `{"mode": "bluetooth"|"wifi", "port": "COM5", "host": "192.168.0.10", "port": 35000}` and stores the connection config in a module-level variable
- `GET /pids` — returns the list of available PIDs from `pids.py`
- Static file serving from `static/` directory

- [ ] **Step 2: Verify main.py imports and basic structure**

Run: `python -c "import main; print('OK')"`
Expected: No import errors

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add FastAPI backend with WebSocket and static serving"
```

---

### Task 3: Create static/index.html

**Files:**
- Create: `static/index.html`

**Interfaces:**
- Consumes: `style.css`, `app.js` (linked as siblings)
- Produces: the dashboard page served at `/`

- [ ] **Step 1: Create static/ directory and index.html**

Create `static/` directory and `static/index.html` with:
- HTML5 boilerplate
- Dark theme (`<html>` with `data-theme="dark"`)
- Top bar: "Kruka OBD Project" title, connection status dot (green/red), Connect/Retry button, COM port input for Bluetooth mode
- Gauges section: three circular SVG gauges for RPM, Speed, Coolant Temp
- Cards section: six numeric cards for Throttle Position, Engine Load, Intake Air Temp, MAF, Fuel Level, Battery Voltage
- Chart section: Plotly.js chart container at the bottom
- Script tags for Plotly.js (CDN), `app.js`

- [ ] **Step 2: Verify HTML structure**

Open `static/index.html` in a browser (file://) — verify all sections render
Expected: Page loads with dark background, gauges, cards, and chart container visible

- [ ] **Step 3: Commit**

```bash
git add static/index.html
git commit -m "feat: create dashboard HTML with gauges, cards, and chart container"
```

---

### Task 4: Create static/style.css

**Files:**
- Create: `static/style.css`

**Interfaces:**
- Consumes: linked from `index.html`
- Produces: dark theme styling for all dashboard elements

- [ ] **Step 1: Create style.css with dark theme, gauge styles, card styles, layout**

Create `static/style.css` with:
- Dark background (`#1a1a2e`), card backgrounds (`#16213e`), text (`#e0e0e0`)
- CSS custom properties for colors: `--bg`, `--card`, `--text`, `--accent`, `--green`, `--red`
- Top bar styling (flexbox, centered title, status dot animation)
- Gauge container (flexbox row, centered)
- SVG gauge styling (circular progress arcs, needle, value text)
- Cards grid (CSS grid, 3 columns on desktop, responsive)
- Card styling (dark bg, rounded corners, label + value)
- Chart container (full width, fixed height)
- Responsive breakpoints for mobile
- Status dot animation (pulse for connected, blink for disconnected)

- [ ] **Step 2: Verify CSS loads**

Open `static/index.html` in browser — verify dark theme applies
Expected: Dark background, styled cards and gauges visible

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: add dark theme CSS with gauges, cards, and responsive layout"
```

---

### Task 5: Create static/app.js

**Files:**
- Create: `static/app.js`

**Interfaces:**
- Consumes: `style.css`, Plotly.js CDN, WebSocket from FastAPI backend
- Produces: live dashboard with real-time updates

- [ ] **Step 1: Create app.js with WebSocket connection and data handling**

Create `static/app.js` with:
- `connectWebSocket()` — opens WebSocket to `/ws`, handles `onmessage` to parse JSON data, calls `updateDashboard(data)`
- `updateDashboard(data)` — updates gauge values, card values, and Plotly chart traces
- `initPlotly()` — creates Plotly chart with empty traces for rpm, speed, coolant_temp, throttle_position, engine_load
- `addPlotlyTrace(timestamp, rpm, speed, coolant, throttle, load)` — appends a data point to all traces
- `setConnectionStatus(connected)` — toggles green/red status dot, shows/hides retry button
- `retryConnection()` — closes existing WebSocket, reconnects after 1s delay
- Auto-connect on page load
- Retry button click handler

- [ ] **Step 2: Verify JS loads without errors**

Open `static/index.html` in browser, check browser console
Expected: No JS errors, WebSocket connection attempted

- [ ] **Step 3: Commit**

```bash
git add static/app.js
git commit -m "feat: add WebSocket client, Plotly chart, and dashboard UI logic"
```

---

### Task 6: Update README with web app instructions

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: existing README.md
- Produces: updated README with web app section

- [ ] **Step 1: Add Web App section to README**

Add a new section "## Web App" after the "Uso" section with:
- How to run the web app: `python main.py`
- Open browser to `http://localhost:8000`
- Auto-connects to the configured scanner
- Retry button if connection drops
- COM port configuration in the UI for Bluetooth mode

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add web app usage instructions to README"
```

---

### Task 7: End-to-end test with mock

**Files:**
- Test: manual integration test

**Interfaces:**
- Consumes: `mock_elm327.py`, `main.py`, `static/` files
- Produces: verified working dashboard

- [ ] **Step 1: Start mock ELM327 server**

Run: `python mock_elm327.py --port 35020`

- [ ] **Step 2: Start the web app**

In another terminal: `python main.py`

- [ ] **Step 3: Open browser and verify**

Open `http://localhost:8000` — verify:
- Page loads with dark theme
- Gauges and cards render
- WebSocket connects and data flows
- Plotly chart updates in real-time
- Connection status shows green

- [ ] **Step 4: Test retry button**

Stop mock server, verify status turns red + retry button appears
Restart mock server, click retry, verify connection restores

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "test: end-to-end test with mock ELM327"
```

---

### Task 8: Deploy to Hugging Face Spaces

**Files:**
- Create: `app.py` (HF Spaces entry point, imports from main.py)
- Create: `requirements.txt` (already done in Task 1)
- Create: `.gitignore` updates if needed

**Interfaces:**
- Consumes: all project files
- Produces: deployed web app on Hugging Face Spaces

- [ ] **Step 1: Create app.py for HF Spaces compatibility**

Create `app.py` that imports and re-exports the FastAPI app from `main.py`:
```python
from main import app
```

- [ ] **Step 2: Push to GitHub**

```bash
git add -A
git commit -m "feat: add Hugging Face Spaces deployment support"
git push origin main
```

- [ ] **Step 3: Create HF Spaces repo and deploy**

- Go to huggingface.co/spaces
- Create new Space, select "Python" SDK
- Upload repo or connect GitHub
- Wait for build to complete

- [ ] **Step 4: Verify deployment**

Open the HF Spaces URL — verify the dashboard loads and works

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add HF Spaces deployment entry point"
```