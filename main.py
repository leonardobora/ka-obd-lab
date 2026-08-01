import asyncio
import math
import os
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pids import PIDS

app = FastAPI()

_connection_config = {}
_START_TIME = time.time()


def _simulated_pid_values():
    t = time.time() - _START_TIME
    return {
        "rpm": round(900 + 60 * math.sin(t)),
        "speed": round(max(0, min(80, t * 4)) if t < 40 else max(0, 80 - (t - 40) * 4)),
        "coolant": round(min(90, 20 + t * 1.5)),
        "throttle": round(12 + 3 * math.sin(t * 2), 1),
        "engine_load": round(25 + 5 * math.sin(t * 1.5), 1),
        "intake_air": round(25 + 4 * math.sin(t * 0.8)),
        "maf": round(2.5 + 1.2 * math.sin(t * 1.3), 2),
        "fuel_level": round(max(0, min(100, 75 - t * 0.05)), 1),
        "battery_voltage": round(13.8 + 0.3 * math.sin(t * 0.5), 1),
    }


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

        if mode == "demo":
            pid_names = list(PIDS.keys())
            while True:
                sim = _simulated_pid_values()
                row = {
                    "rpm": sim["rpm"],
                    "speed": sim["speed"],
                    "coolant_temp": sim["coolant"],
                    "throttle_position": sim["throttle"],
                    "engine_load": sim["engine_load"],
                    "intake_air_temp": sim["intake_air"],
                    "maf": sim["maf"],
                    "fuel_level": sim["fuel_level"],
                    "battery_voltage": sim["battery_voltage"],
                }
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

            pid_names = list(PIDS.keys())
            while True:
                row = {}
                for name in pid_names:
                    try:
                        value = client.query_pid(name)
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
async def pids_endpoint():
    return list(PIDS.keys())


if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)