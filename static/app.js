let ws = null;
let plotlyInitialized = false;
let plotlyDiv = null;
const MAX_POINTS = 200;
let connectionState = "disconnected"; // disconnected, connecting, connected, error
let lastDataTime = 0;
let dataTimeout = null;

function getConfig() {
    const mode = document.getElementById("mode-select").value;
    const comPort = document.getElementById("com-port").value;
    const wifiAddr = document.getElementById("wifi-addr").value;
    const parts = wifiAddr.split(":");
    return { mode, comPort, wifiHost: parts[0], wifiPort: parts[1] || "35000" };
}

function setConnectionState(state, message) {
    connectionState = state;
    const dot = document.getElementById("status-dot");
    const text = document.getElementById("status-text");
    const badge = document.getElementById("connection-badge");
    
    dot.className = "status-dot " + state;
    text.textContent = message || state.charAt(0).toUpperCase() + state.slice(1);
    
    badge.className = "connection-badge " + state;
    badge.textContent = state === "connected" ? "ONLINE" : 
                        state === "connecting" ? "CONNECTING" : 
                        state === "error" ? "ERROR" : "OFFLINE";
}

function checkDataTimeout() {
    if (connectionState === "connected" && Date.now() - lastDataTime > 3000) {
        setConnectionState("error", "Car disconnected");
        document.querySelectorAll(".card").forEach(card => {
            card.classList.add("warning");
        });
    }
}

function connectWebSocket() {
    const config = getConfig();
    const host = window.location.host;
    const wsUrl = "ws://" + host + "/ws";

    if (ws) {
        try {
            ws.close();
        } catch (e) {}
        ws = null;
    }

    setConnectionState("connecting", "Connecting to " + config.mode + "...");
    
    // Reset card warnings
    document.querySelectorAll(".card").forEach(card => {
        card.classList.remove("warning", "error");
    });

    ws = new WebSocket(wsUrl);

    ws.onopen = function () {
        const payload = { mode: config.mode };
        if (config.mode === "bluetooth") {
            payload.port = config.comPort;
        } else if (config.mode === "wifi") {
            payload.host = config.wifiHost;
            payload.port = parseInt(config.wifiPort, 10) || 35000;
        }
        ws.send(JSON.stringify(payload));
        setConnectionState("connected", "Connected via " + config.mode);
        lastDataTime = Date.now();
        
        // Start timeout checker
        if (dataTimeout) clearInterval(dataTimeout);
        dataTimeout = setInterval(checkDataTimeout, 1000);
    };

    ws.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
            if (data.error) {
                setConnectionState("error", data.error);
                return;
            }
            lastDataTime = Date.now();
            updateDashboard(data);
        } catch (e) {
            console.error("Failed to parse message:", e);
        }
    };

    ws.onclose = function () {
        setConnectionState("disconnected", "Disconnected");
        if (dataTimeout) clearInterval(dataTimeout);
    };

    ws.onerror = function (err) {
        console.error("WebSocket error:", err);
        setConnectionState("error", "Connection failed");
    };
}

function updateDashboard(data) {
    // Gauges - handle NaN
    updateGauge("gauge-rpm-text", data.rpm != null ? Math.round(data.rpm) : "--");
    updateGauge("gauge-speed-text", data.speed != null ? Math.round(data.speed) : "--");
    updateGauge("gauge-coolant-text", data.coolant_temp != null ? Math.round(data.coolant_temp) : "--");
    updateGaugeArc("gauge-rpm-arc", data.rpm || 0, 8000);
    updateGaugeArc("gauge-speed-arc", data.speed || 0, 200);
    updateGaugeArc("gauge-coolant-arc", data.coolant_temp || 0, 120);

    // Cards - handle NaN with visual feedback
    updateCardWithStatus("val-throttle", "card-throttle", data.throttle_position, "%");
    updateCardWithStatus("val-engine-load", "card-engine-load", data.engine_load, "%");
    updateCardWithStatus("val-intake-air", "card-intake-air", data.intake_air_temp, "°C");
    updateCardWithStatus("val-maf", "card-maf", data.maf, " g/s");
    updateCardWithStatus("val-fuel", "card-fuel", data.fuel_level, "%");
    updateCardWithStatus("val-battery", "card-battery", data.battery_voltage, " V");

    addPlotlyTrace(
        data.timestamp || Date.now(),
        data.rpm,
        data.speed,
        data.coolant_temp,
        data.throttle_position,
        data.engine_load
    );
}

    addPlotlyTrace(
        data.timestamp || Date.now(),
        data.rpm,
        data.speed,
        data.coolant_temp,
        data.throttle_position,
        data.engine_load
    );
}

function updateGauge(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = value;
}

function updateGaugeArc(id, value, max) {
    const el = document.getElementById(id);
    if (!el) return;
    const pct = Math.min(1, Math.max(0, value / max));
    const total = 502.65;
    el.setAttribute("stroke-dashoffset", total * (1 - pct));
}

function updateCard(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    if (typeof value === 'string' && value.includes('Error')) {
        el.textContent = "--";
    } else {
        el.textContent = value;
    }
}

function updateCardWithStatus(valueId, cardId, value, unit) {
    const el = document.getElementById(valueId);
    const card = document.getElementById(cardId);
    if (!el || !card) return;
    
    card.classList.remove("warning", "error");
    
    if (value == null || isNaN(value)) {
        el.textContent = "--";
        el.classList.add("na");
        card.classList.add("warning");
    } else {
        el.textContent = typeof value === 'number' ? 
            (Number.isInteger(value) ? value : value.toFixed(1)) + unit : 
            value + unit;
        el.classList.remove("na");
    }
}

function initPlotly() {
    const traces = [
        { x: [], y: [], name: "rpm", type: "scatter", mode: "lines" },
        { x: [], y: [], name: "speed", type: "scatter", mode: "lines" },
        { x: [], y: [], name: "coolant_temp", type: "scatter", mode: "lines" },
        { x: [], y: [], name: "throttle_position", type: "scatter", mode: "lines" },
        { x: [], y: [], name: "engine_load", type: "scatter", mode: "lines" },
    ];

    const layout = {
        paper_bgcolor: "#1a1a2e",
        plot_bgcolor: "#1a1a2e",
        font: { color: "#e0e0e0" },
        xaxis: {
            title: "Time",
            color: "#e0e0e0",
            gridcolor: "#333",
        },
        yaxis: {
            title: "Value",
            color: "#e0e0e0",
            gridcolor: "#333",
        },
        legend: {
            font: { color: "#e0e0e0" },
        },
        margin: { l: 50, r: 20, t: 40, b: 40 },
    };

    const config = {
        responsive: true,
        displayModeBar: false,
    };

    plotlyDiv = document.getElementById("chart");
    if (!plotlyDiv) return;

    Plotly.newPlot(plotlyDiv, traces, layout, config);
    plotlyInitialized = true;
}

function addPlotlyTrace(timestamp, rpm, speed, coolant, throttle, load) {
    if (!plotlyInitialized || !plotlyDiv) return;

    const timeStr = new Date(timestamp).toLocaleTimeString();

    Plotly.extendTraces(plotlyDiv, {
        x: [[timeStr], [timeStr], [timeStr], [timeStr], [timeStr]],
        y: [[rpm], [speed], [coolant], [throttle], [load]],
    }, [0, 1, 2, 3, 4]);

    const traceCount = plotlyDiv.data.length;
    const currentLen = plotlyDiv.data[0].x.length;

    if (currentLen > MAX_POINTS) {
        Plotly.relayout(plotlyDiv, {
            xaxis: {
                range: [currentLen - MAX_POINTS, currentLen],
            },
        });
    }
}

function retryConnection() {
    if (ws) {
        try {
            ws.close();
        } catch (e) {}
        ws = null;
    }
    setTimeout(function () {
        connectWebSocket();
    }, 1000);
}

function init() {
    initPlotly();
    setConnectionState("disconnected");
    
    const connectBtn = document.getElementById("connect-btn");
    if (connectBtn) {
        connectBtn.addEventListener("click", connectWebSocket);
    }
    
    const retryBtn = document.getElementById("retry-btn");
    if (retryBtn) {
        retryBtn.addEventListener("click", retryConnection);
    }
}

window.addEventListener("load", init);