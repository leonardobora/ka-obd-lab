"""Cliente ELM327 minimalista: fala AT/OBD cru por WiFi (TCP) ou serial (BT/USB COM port).

Sem dependencia de python-obd de proposito -- assim a gente ve exatamente
o que esta sendo enviado/recebido no barramento, o que ajuda quando o
objetivo e entender o protocolo (e nao so ler numeros bonitos num app).
"""
import socket
import time

from pids import PIDS


class ELM327Error(RuntimeError):
    pass


class ELM327Client:
    def __init__(self, io_obj):
        self._io = io_obj

    @classmethod
    def wifi(cls, host="192.168.0.10", port=35000, timeout=5):
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.settimeout(timeout)
        return cls(sock.makefile("rwb", buffering=0))

    @classmethod
    def serial(cls, com_port, baudrate=9600, timeout=5):
        import serial

        ser = serial.Serial(com_port, baudrate=baudrate, timeout=timeout)
        return cls(ser)

    def _read_until_prompt(self, timeout=5):
        """Le bytes ate encontrar o prompt '>' que o ELM327 manda ao fim de cada resposta."""
        deadline = time.time() + timeout
        buf = b""
        while time.time() < deadline:
            try:
                chunk = self._io.read(1)
            except (socket.timeout, TimeoutError, OSError):
                break
            if not chunk:
                break
            buf += chunk
            if b">" in buf:
                break
        return buf

    def send(self, command: str) -> str:
        self._io.write((command + "\r").encode())
        raw = self._read_until_prompt()
        text = raw.decode(errors="replace").replace(">", "")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines and lines[0].upper().replace(" ", "") == command.upper().replace(" ", ""):
            lines = lines[1:]
        return " ".join(lines)

    def initialize(self):
        """Reset + configuracao basica. ATSP0 = deixa o adaptador auto-detectar o protocolo."""
        responses = {}
        for cmd in ("ATZ", "ATE0", "ATL0", "ATS0", "ATH0", "ATSP0"):
            responses[cmd] = self.send(cmd)
            time.sleep(0.1)
        time.sleep(1)
        return responses

    def query_pid(self, name: str, pids: dict = None) -> float:
        spec = (pids or PIDS)[name]
        response = self.send(f"{spec['mode']}{spec['pid']}")
        data_bytes = _extract_data_bytes(response, spec["mode"], spec["pid"], spec["bytes"])
        return spec["decode"](data_bytes)

    def close(self):
        self._io.close()


def _extract_data_bytes(response: str, mode: str, pid: str, expected_len: int) -> list:
    """A resposta pode vir como '41 0C 1A F8' (com espacos) ou '410C1A85' (sem espacos).
    Pode tambem incluir 'SEARCHING...' como prefixo enquanto o adaptador conecta ao ECU."""
    response = response.upper()
    # Remove prefixos de status que podem aparecer antes dos dados reais
    for prefix in ("SEARCHING...", "UNABLE TO CONNECT", "NO DATA"):
        if prefix in response:
            response = response.split(prefix, 1)[1].strip()
    hex_chars = "".join(c for c in response if c in "0123456789ABCDEF")
    hex_tokens = [hex_chars[i:i+2] for i in range(0, len(hex_chars), 2) if len(hex_chars[i:i+2]) == 2]
    try:
        pid_index = hex_tokens.index(pid.upper())
    except ValueError:
        raise ELM327Error(f"Resposta inesperada para PID {pid}: '{response}'")
    data_hex = hex_tokens[pid_index + 1: pid_index + 1 + expected_len]
    if len(data_hex) < expected_len:
        raise ELM327Error(f"Resposta curta para PID {pid}: '{response}'")
    return [int(h, 16) for h in data_hex]
