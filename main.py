import asyncio
import math
import os
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pids import PIDS

# Vehicle-specific PID sets
VEHICLE_PIDS = {
    "ford_ka_2017": PIDS,  # default (Ka 2017)
}

try:
    from pids_corolla2024 import COROLLA_2024_PIDS
    VEHICLE_PIDS["corolla_2024"] = COROLLA_2024_PIDS
except ImportError:
    pass

try:
    from pids_etios import ETIOS_13_PIDS
    VEHICLE_PIDS["etios_13"] = ETIOS_13_PIDS
except ImportError:
    pass

VEHICLE_LABELS = {
    "ford_ka_2017": "Ford Ka 2017 (Fiat)",
    "corolla_2024": "Toyota Corolla XEI 2024",
    "etios_13": "Toyota Etios 1.3",
}

app = FastAPI()

_connection_config = {}
_START_TIME = time.time()


def _simulated_pid_values(vehicle="ford_ka_2017"):
    t = time.time() - _START_TIME
    base = {
        "rpm": round(900 + 60 * math.sin(t)),
        "speed": round(max(0, min(80, t * 4)) if t < 40 else max(0, 80 - (t - 40) * 4)),
        "coolant_temp": round(min(90, 20 + t * 1.5)),
        "throttle_position": round(12 + 3 * math.sin(t * 2), 1),
        "engine_load": round(25 + 5 * math.sin(t * 1.5), 1),
        "intake_air_temp": round(25 + 4 * math.sin(t * 0.8)),
        "maf": round(2.5 + 1.2 * math.sin(t * 1.3), 2) if vehicle == "ford_ka_2017" else round(8.5 + 3 * math.sin(t * 1.3), 2),
        "fuel_level": round(max(0, min(100, 75 - t * 0.05)), 1),
        "battery_voltage": round(13.8 + 0.3 * math.sin(t * 0.5), 1),
        "fuel_trim_short_bank1": round(2 + 3 * math.sin(t * 0.7), 1),
        "fuel_trim_long_bank1": round(1.5 + 1.5 * math.sin(t * 0.3), 1),
        "fuel_trim_short_bank2": None,
        "fuel_trim_long_bank2": None,
        "o2_sensor1_voltage": round(0.45 + 0.35 * math.sin(t * 1.1), 2),
        "o2_sensor2_voltage": round(0.45 + 0.35 * math.sin(t * 1.1 + 1), 2),
        "timing_advance": round(10 + 8 * math.sin(t * 0.9), 1),
        "run_time": round(t) % 3600,
        "fuel_system_status": "Closed (loop)",
        "dtc_codes": [],
    }
    # Corolla extras
    if vehicle == "corolla_2024":
        base["vvt_intake_angle"] = round(15 + 10 * math.sin(t * 0.6), 1)
        base["vvt_exhaust_angle"] = round(8 + 5 * math.sin(t * 0.5), 1)
        base["knock_retard"] = round(0.5 * math.sin(t * 0.3), 2)
        base["hpfp_duty_cycle"] = round(45 + 15 * math.sin(t * 0.8), 1)
        base["wheel_speed_fl"] = base["speed"]
        base["wheel_speed_fr"] = base["speed"]
        base["wheel_speed_rl"] = base["speed"]
        base["wheel_speed_rr"] = base["speed"]
        base["yaw_rate"] = round(2 * math.sin(t * 0.4), 1)
        base["lateral_g"] = round(0.1 * math.sin(t * 0.4), 2)
        base["steering_angle"] = round(15 * math.sin(t * 0.3), 1)
    # Etios extras
    elif vehicle == "etios_13":
        base["map_pressure"] = round(45 + 20 * math.sin(t * 0.7))
        base["absolute_throttle_b"] = base["throttle_position"]
        base["accelerator_pedal_d"] = round(10 + 5 * math.sin(t * 2), 1)
        base["accelerator_pedal_e"] = round(10 + 5 * math.sin(t * 2), 1)
        base["commanded_throttle"] = base["throttle_position"]
        base["relative_throttle"] = round(5 + 3 * math.sin(t * 2), 1)
        base["barometric_pressure"] = 101
        base["catalyst_temp_b1s1"] = round(300 + 50 * math.sin(t * 0.2))
        base["catalyst_temp_b1s2"] = round(280 + 40 * math.sin(t * 0.2))
        base["commanded_evap_purge"] = round(30 + 20 * math.sin(t * 0.4), 1)
        base["time_run_with_mil"] = 0
        base["time_since_codes_cleared"] = 500
        base["distance_with_mil"] = 0
        base["warmups_since_clear"] = 50
    return base


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = None
    try:
        data = await websocket.receive_json()
        mode = data.get("mode")
        vehicle = data.get("vehicle", "ford_ka_2017")
        pids = VEHICLE_PIDS.get(vehicle, PIDS)

        if mode == "demo":
            pid_names = list(pids.keys())
            while True:
                sim = _simulated_pid_values(vehicle)
                row = {k: sim.get(k) for k in pid_names}
                row["dtc_codes"] = []
                await websocket.send_json(row)
                await asyncio.sleep(0.5)
        else:
            from obd_client import ELM327Client

            if mode == "bluetooth":
                port = data.get("port", "COM5")
                client = ELM327Client.serial(port)
            elif mode == "wifi":
                host = data.get("host", "192.168.0.10")
                port = data.get("port", 35000)
                client = ELM327Client.wifi(host, port)
            else:
                await websocket.send_json({"error": f"Unknown mode: {mode}"})
                return

            client.initialize()

            pid_names = list(pids.keys())
            while True:
                row = {}
                for name in pid_names:
                    try:
                        value = client.query_pid(name, pids)
                        row[name] = round(value, 2) if isinstance(value, float) else value
                    except Exception:
                        row[name] = None
                await websocket.send_json(row)
                await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"error": str(exc)})
        except Exception:
            pass
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


@app.post("/connect")
async def connect_endpoint(data: dict):
    global _connection_config
    _connection_config = data
    return {"status": "ok", "config": data}


@app.get("/pids")
async def pids_endpoint(vehicle: str = "ford_ka_2017"):
    pids = VEHICLE_PIDS.get(vehicle, PIDS)
    return list(pids.keys())


@app.get("/vehicles")
async def vehicles_endpoint():
    return [{"id": k, "label": v, "pid_count": len(VEHICLE_PIDS.get(k, {}))} for k, v in VEHICLE_LABELS.items()]


@app.post("/dtc")
async def read_dtc_endpoint(data: dict):
    """Read Diagnostic Trouble Codes via Mode 03."""
    mode = data.get("mode")
    client = None
    try:
        from obd_client import ELM327Client
        if mode == "bluetooth":
            port = data.get("port", "COM5")
            client = ELM327Client.serial(port)
        elif mode == "wifi":
            host = data.get("host", "192.168.0.10")
            port = data.get("port", 35000)
            client = ELM327Client.wifi(host, port)
        else:
            return {"error": "Unknown mode"}

        client.initialize()
        response = client.send("03")
        dtcs = _parse_dtc_response(response)
        return {"codes": dtcs, "raw": response}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if client:
            try:
                client.close()
            except Exception:
                pass


def _parse_dtc_response(response: str) -> list:
    """Parse Mode 03 response into DTC code strings like P0300, C0035, etc."""
    response = response.upper()
    for prefix in ("SEARCHING...", "UNABLE TO CONNECT", "NO DATA", "43"):
        response = response.replace(prefix, "")
    hex_chars = "".join(c for c in response if c in "0123456789ABCDEF")
    hex_tokens = [hex_chars[i:i+2] for i in range(0, len(hex_chars), 2) if len(hex_chars[i:i+2]) == 2]
    dtcs = []
    prefix_map = {"0": "P", "1": "P", "2": "P", "3": "P",
                  "4": "C", "5": "C", "6": "C", "7": "C",
                  "8": "B", "9": "B", "A": "B", "B": "B",
                  "C": "U", "D": "U", "E": "U", "F": "U"}
    i = 0
    while i + 1 < len(hex_tokens):
        b1 = int(hex_tokens[i], 16)
        b2 = int(hex_tokens[i + 1], 16)
        if b1 == 0 and b2 == 0:
            i += 2
            continue
        letter = prefix_map.get(hex_tokens[i][0], "P")
        code = f"{letter}{b1 & 0x3F:01X}{b2:02X}"
        dtcs.append(code)
        i += 2
    return dtcs


if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)