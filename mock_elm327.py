"""Simula um adaptador ELM327 em modo WiFi, pra validar obd_client.py/read_live.py
sem precisar do scanner fisico. Gera valores que variam com o tempo (RPM oscilando,
temperatura subindo ate a temperatura de operacao, etc) pra provar que o parsing
esta correto e nao so retornando um numero fixo por acaso.

Uso:
    python mock_elm327.py --port 35000
    (em outro terminal) python read_live.py --wifi --host 127.0.0.1 --port 35000
"""
import argparse
import math
import socketserver
import time

START_TIME = time.time()


def _simulated_values():
    t = time.time() - START_TIME
    rpm = 900 + 60 * math.sin(t)
    speed = max(0, min(80, t * 4)) if t < 40 else max(0, 80 - (t - 40) * 4)
    coolant = min(90, 20 + t * 1.5)
    throttle = 12 + 3 * math.sin(t * 2)
    engine_load = 25 + 5 * math.sin(t * 1.5)
    return {
        "0C": _encode_2byte(rpm * 4),
        "0D": _encode_1byte(speed),
        "05": _encode_1byte(coolant + 40),
        "11": _encode_1byte(throttle * 255 / 100),
        "04": _encode_1byte(engine_load * 255 / 100),
    }


def _encode_1byte(value):
    return f"{int(round(value)) & 0xFF:02X}"


def _encode_2byte(value):
    v = int(round(value)) & 0xFFFF
    return f"{(v >> 8) & 0xFF:02X} {v & 0xFF:02X}"


class ELM327Handler(socketserver.BaseRequestHandler):
    def setup(self):
        self.echo_on = True

    def handle(self):
        buf = b""
        while True:
            chunk = self.request.recv(1)
            if not chunk:
                break
            buf += chunk
            if buf.endswith(b"\r"):
                cmd = buf.strip().decode(errors="replace")
                buf = b""
                self._respond(cmd)

    def _respond(self, cmd):
        upper = cmd.upper()
        out = ""
        if self.echo_on:
            out += cmd + "\r\n"

        if upper == "ATZ":
            out += "ELM327 v2.1\r\r"
        elif upper == "ATE0":
            self.echo_on = False
            out += "OK\r\r"
        elif upper.startswith("AT"):
            out += "OK\r\r"
        elif len(upper) == 4 and upper[:2] == "01":
            pid = upper[2:]
            values = _simulated_values()
            if pid in values:
                out += f"41 {pid} {values[pid]}\r\r"
            else:
                out += "NO DATA\r\r"
        else:
            out += "?\r\r"

        out += ">"
        self.request.sendall(out.encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=35000)
    args = parser.parse_args()

    server = socketserver.ThreadingTCPServer((args.host, args.port), ELM327Handler)
    print(f"Mock ELM327 escutando em {args.host}:{args.port} (Ctrl+C pra parar)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando mock.")


if __name__ == "__main__":
    main()
