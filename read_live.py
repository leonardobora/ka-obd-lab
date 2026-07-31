"""Le PIDs em loop e imprime no terminal.

Uso:
    python read_live.py --wifi                      # modo WiFi, host/porta padrao do adaptador
    python read_live.py --wifi --host 192.168.0.10 --port 35000
    python read_live.py --serial COM5                # modo Bluetooth/USB pareado como COM port
    python read_live.py --wifi --host 127.0.0.1 --port 35000   # contra o mock_elm327.py
"""
import argparse
import time

from obd_client import ELM327Client
from pids import PIDS

DEFAULT_SIGNALS = ["rpm", "speed", "coolant_temp", "throttle_position", "engine_load"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wifi", action="store_true", help="conectar via WiFi (TCP)")
    parser.add_argument("--host", default="192.168.0.10")
    parser.add_argument("--port", type=int, default=35000)
    parser.add_argument("--serial", metavar="COM_PORT", help="conectar via serial (ex: COM5)")
    parser.add_argument("--interval", type=float, default=1.0, help="segundos entre leituras")
    parser.add_argument("--signals", nargs="+", default=DEFAULT_SIGNALS, choices=list(PIDS.keys()))
    args = parser.parse_args()

    if args.serial:
        client = ELM327Client.serial(args.serial)
    else:
        client = ELM327Client.wifi(args.host, args.port)

    print("Inicializando adaptador...")
    init_responses = client.initialize()
    for cmd, resp in init_responses.items():
        print(f"  {cmd} -> {resp}")

    print(f"\nLendo {', '.join(args.signals)} a cada {args.interval}s (Ctrl+C pra parar)\n")
    try:
        while True:
            row = []
            for name in args.signals:
                spec = PIDS[name]
                try:
                    value = client.query_pid(name)
                    row.append(f"{name}={value:.1f}{spec['unit']}")
                except Exception as exc:
                    row.append(f"{name}=ERRO({exc})")
            print(" | ".join(row))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nEncerrando.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
