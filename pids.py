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
    # --- Fuel Trims ---
    "fuel_trim_short_bank1": {
        "mode": "01",
        "pid": "06",
        "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%",
    },
    "fuel_trim_long_bank1": {
        "mode": "01",
        "pid": "07",
        "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%",
    },
    "fuel_trim_short_bank2": {
        "mode": "01",
        "pid": "08",
        "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%",
    },
    "fuel_trim_long_bank2": {
        "mode": "01",
        "pid": "09",
        "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%",
    },
    # --- O2 Sensors ---
    "o2_sensor1_voltage": {
        "mode": "01",
        "pid": "14",
        "bytes": 2,
        "decode": lambda b: b[0] / 200,
        "unit": "V",
    },
    "o2_sensor2_voltage": {
        "mode": "01",
        "pid": "15",
        "bytes": 2,
        "decode": lambda b: b[0] / 200,
        "unit": "V",
    },
    # --- Timing & Runtime ---
    "timing_advance": {
        "mode": "01",
        "pid": "0E",
        "bytes": 1,
        "decode": lambda b: (b[0] - 128) / 2,
        "unit": "°",
    },
    "run_time": {
        "mode": "01",
        "pid": "1F",
        "bytes": 2,
        "decode": lambda b: (b[0] * 256) + b[1],
        "unit": "s",
    },
    "fuel_system_status": {
        "mode": "01",
        "pid": "03",
        "bytes": 2,
        "decode": lambda b: "Open (normal)" if b[0] == 1 else "Closed (loop)" if b[0] == 2 else "Open (warmup)" if b[0] == 4 else f"Status {b[0]}",
        "unit": "",
    },
}
