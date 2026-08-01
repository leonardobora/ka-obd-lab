import asyncio
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from obd_client import ELM327Client
from pids import PIDS

app = FastAPI()

_connection_config = {}


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
                    row[name] = value
                except Exception as exc:
                    row[name] = str(exc)
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