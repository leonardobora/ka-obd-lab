"""Le PIDs em loop e imprime no terminal.

Uso:
    python read_live.py --wifi                      # modo WiFi, host/porta padrao do adaptador
    python read_live.py --wifi --host 192.168.0.10 --port 35000
    python read_live.py --bluetooth COM5             # modo Bluetooth pareado como COM port
    python read_live.py --bluetooth COM5 --baud 115200
    python read_live.py --wifi --host 127.0.0.1 --port 35000   # contra o mock_elm327.py
"""
import argparse
import time

from obd_client import ELM327Client
from pids import PIDS

DEFAULT_SIGNALS = ["rpm", "speed", "coolant_temp", "throttle_position", "engine_load"]


def _connect_wifi(host, port):
    return ELM327Client.wifi(host, port)


def _connect_bluetooth(com_port, baudrate):
    return ELM327Client.serial(com_port, baudrate=baudrate)


def _connect(args):
    if args.wifi:
        return _connect_wifi(args.host, args.port)
    return _connect_bluetooth(args.bluetooth, args.baud)


def _run(args):
    while True:
        try:
            client = _connect(args)
            print("Inicializando adaptador...")
            init_responses = client.initialize()
            for cmd, resp in init_responses.items():
                print(f"  {cmd} -> {resp}")
            break
        except Exception as exc:
            print(f"Falha ao conectar: {exc}")
            if args.bluetooth:
                print(f"Tentando novamente em {args.reconnect_delay}s...")
                time.sleep(args.reconnect_delay)
            else:
                raise

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
    except (OSError, ConnectionError) as exc:
        print(f"\nConexao perdida: {exc}")
    finally:
        try:
            client.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wifi", action="store_true", help="conectar via WiFi (TCP)")
    parser.add_argument("--bluetooth", metavar="COM_PORT", help="conectar via Bluetooth serial (ex: COM5)")
    parser.add_argument("--baud", type=int, default=9600, help="baud rate para serial/Bluetooth (padrao: 9600)")
    parser.add_argument("--host", default="192.168.0.10")
    parser.add_argument("--port", type=int, default=35000)
    parser.add_argument("--interval", type=float, default=1.0, help="segundos entre leituras")
    parser.add_argument("--signals", nargs="+", default=DEFAULT_SIGNALS, choices=list(PIDS.keys()))
    parser.add_argument("--reconnect-delay", type=float, default=3.0, help="segundos entre tentativas de reconexao")
    args = parser.parse_args()

    if not args.wifi and not args.bluetooth:
        parser.error("Escolha --wifi ou --bluetooth COM_PORT")

    while True:
        _run(args)
        if not args.bluetooth:
            break
        print(f"\nReconectando em {args.reconnect_delay}s...")
        time.sleep(args.reconnect_delay)


if __name__ == "__main__":
    main()
