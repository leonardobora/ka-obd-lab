"""Definicoes de PIDs OBD-II padrao (Modo 01) usados nas leituras iniciais.

Cada entrada: (mode, pid) -> (num_bytes_esperados, funcao_de_decodificacao, unidade)
Referencia: SAE J1979 / Modo 01.
"""

PIDS = {
    "rpm": {
        "mode": "01",
        "pid": "0C",
        "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 4,
        "unit": "rpm",
    },
    "speed": {
        "mode": "01",
        "pid": "0D",
        "bytes": 1,
        "decode": lambda b: b[0],
        "unit": "km/h",
    },
    "coolant_temp": {
        "mode": "01",
        "pid": "05",
        "bytes": 1,
        "decode": lambda b: b[0] - 40,
        "unit": "C",
    },
    "throttle_position": {
        "mode": "01",
        "pid": "11",
        "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%",
    },
    "intake_air_temp": {
        "mode": "01",
        "pid": "0F",
        "bytes": 1,
        "decode": lambda b: b[0] - 40,
        "unit": "C",
    },
    "engine_load": {
        "mode": "01",
        "pid": "04",
        "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%",
    },
    "maf": {
        "mode": "01",
        "pid": "10",
        "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "g/s",
    },
    "fuel_level": {
        "mode": "01",
        "pid": "2F",
        "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%",
    },
    "battery_voltage": {
        "mode": "01",
        "pid": "42",
        "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 1000,
        "unit": "V",
    },
}
