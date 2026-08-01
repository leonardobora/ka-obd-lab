let ws = null;
let plotlyInitialized = false;
let plotlyDiv = null;
const MAX_POINTS = 200;

function getConfig() {
    const mode = document.getElementById("mode").value;
    const comPort = document.getElementById("com-port").value;
    const wifiHost = document.getElementById("wifi-host").value;
    const wifiPort = document.getElementById("wifi-port").value;
    return { mode, comPort, wifiHost, wifiPort };
}

function connectWebSocket() {
    const config = getConfig();
    const host = window.location.host;
    const wsUrl = "ws://" + host + "/ws";

    if (ws) {
        try {
            ws.close();
        } catch (e) {
            // ignore
        }
        ws = null;
    }

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
        setConnectionStatus(true);
    };

    ws.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
            if (data.error) {
                console.error("WebSocket error:", data.error);
                return;
            }
            updateDashboard(data);
        } catch (e) {
            console.error("Failed to parse message:", e);
        }
    };

    ws.onclose = function () {
        setConnectionStatus(false);
    };

    ws.onerror = function (err) {
        console.error("WebSocket error:", err);
        setConnectionStatus(false);
    };
}

function updateDashboard(data) {
    updateGauge("gauge-rpm", data.rpm);
    updateGauge("gauge-speed", data.speed);
    updateGauge("gauge-coolant", data.coolant_temp);

    updateCard("card-throttle", data.throttle_position);
    updateCard("card-load", data.engine_load);
    updateCard("card-iat", data.intake_air_temp);
    updateCard("card-maf", data.maf);
    updateCard("card-fuel", data.fuel_level);
    updateCard("card-battery", data.battery_voltage);

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

function updateCard(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = value;
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

    plotlyDiv = document.getElementById("plotly-chart");
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

function setConnectionStatus(connected) {
    const dot = document.getElementById("status-dot");
    const retryBtn = document.getElementById("retry-btn");

    if (dot) {
        dot.style.backgroundColor = connected ? "#2ecc71" : "#e74c3c";
    }

    if (retryBtn) {
        retryBtn.style.display = connected ? "none" : "inline-block";
    }
}

function retryConnection() {
    if (ws) {
        try {
            ws.close();
        } catch (e) {
            // ignore
        }
        ws = null;
    }
    setTimeout(function () {
        connectWebSocket();
    }, 1000);
}

function init() {
    initPlotly();
    connectWebSocket();

    const retryBtn = document.getElementById("retry-btn");
    if (retryBtn) {
        retryBtn.addEventListener("click", retryConnection);
    }
}

window.addEventListener("load", init);