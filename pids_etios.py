"""PIDs Toyota Etios 1.3 (Motor 3NR-FE - Flex, 86cv).

PIDs confirmados funcionando via ELM327 + CAN 11-bit (ISO 15765-4).
O Etios tem painel digital (versao Top/Limitada) e suporta bem OBD-II generico.
Referencia: repositorio eron93br/carOBD (dataset OBD-II do Etios 2014).
"""

ETIOS_13_PIDS = {
    # ==================== MODE 01 - Genericos ====================
    "rpm": {
        "mode": "01", "pid": "0C", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 4,
        "unit": "rpm", "label": "RPM",
    },
    "speed": {
        "mode": "01", "pid": "0D", "bytes": 1,
        "decode": lambda b: b[0],
        "unit": "km/h", "label": "Speed",
    },
    "coolant_temp": {
        "mode": "01", "pid": "05", "bytes": 1,
        "decode": lambda b: b[0] - 40,
        "unit": "°C", "label": "Coolant Temp",
    },
    "throttle_position": {
        "mode": "01", "pid": "11", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Throttle",
    },
    "intake_air_temp": {
        "mode": "01", "pid": "0F", "bytes": 1,
        "decode": lambda b: b[0] - 40,
        "unit": "°C", "label": "Intake Air",
    },
    "engine_load": {
        "mode": "01", "pid": "04", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Engine Load",
    },
    "fuel_level": {
        "mode": "01", "pid": "2F", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Fuel Level",
    },
    "battery_voltage": {
        "mode": "01", "pid": "42", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 1000,
        "unit": "V", "label": "Battery",
    },
    "fuel_trim_short_bank1": {
        "mode": "01", "pid": "06", "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%", "label": "Short Fuel Trim",
    },
    "fuel_trim_long_bank1": {
        "mode": "01", "pid": "07", "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%", "label": "Long Fuel Trim",
    },
    "timing_advance": {
        "mode": "01", "pid": "0E", "bytes": 1,
        "decode": lambda b: (b[0] - 128) / 2,
        "unit": "°", "label": "Timing Advance",
    },
    "run_time": {
        "mode": "01", "pid": "1F", "bytes": 2,
        "decode": lambda b: (b[0] * 256) + b[1],
        "unit": "s", "label": "Run Time",
    },
    "fuel_system_status": {
        "mode": "01", "pid": "03", "bytes": 2,
        "decode": lambda b: "Open (normal)" if b[0] == 1 else "Closed (loop)" if b[0] == 2 else "Open (warmup)" if b[0] == 4 else f"Status {b[0]}",
        "unit": "", "label": "Fuel System",
    },
    "o2_sensor1_voltage": {
        "mode": "01", "pid": "14", "bytes": 2,
        "decode": lambda b: b[0] / 200,
        "unit": "V", "label": "O2 Sensor 1",
    },
    "o2_sensor2_voltage": {
        "mode": "01", "pid": "15", "bytes": 2,
        "decode": lambda b: b[0] / 200,
        "unit": "V", "label": "O2 Sensor 2",
    },

    # ==================== MODE 01 - Etios Especificos ====================
    # Confirmados no dataset eron93br/carOBD
    "map_pressure": {
        "mode": "01", "pid": "0B", "bytes": 1,
        "decode": lambda b: b[0],
        "unit": "kPa", "label": "MAP",
    },
    "absolute_throttle_b": {
        "mode": "01", "pid": "47", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Throttle B",
    },
    "accelerator_pedal_d": {
        "mode": "01", "pid": "49", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Pedal D",
    },
    "accelerator_pedal_e": {
        "mode": "01", "pid": "4A", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Pedal E",
    },
    "commanded_throttle": {
        "mode": "01", "pid": "4C", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Cmd Throttle",
    },
    "relative_throttle": {
        "mode": "01", "pid": "45", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "Rel Throttle",
    },
    "barometric_pressure": {
        "mode": "01", "pid": "33", "bytes": 1,
        "decode": lambda b: b[0],
        "unit": "kPa", "label": "Barometric",
    },
    "module_voltage": {
        "mode": "01", "pid": "42", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 1000,
        "unit": "V", "label": "ECU Voltage",
    },
    "catalyst_temp_b1s1": {
        "mode": "01", "pid": "3C", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 10 - 40,
        "unit": "°C", "label": "Catalyst B1S1",
    },
    "catalyst_temp_b1s2": {
        "mode": "01", "pid": "3E", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 10 - 40,
        "unit": "°C", "label": "Catalyst B1S2",
    },
    "commanded_evap_purge": {
        "mode": "01", "pid": "2E", "bytes": 1,
        "decode": lambda b: (b[0] * 100) / 255,
        "unit": "%", "label": "EVAP Purge",
    },
    "time_run_with_mil": {
        "mode": "01", "pid": "4D", "bytes": 2,
        "decode": lambda b: (b[0] * 256) + b[1],
        "unit": "min", "label": "Time w/ MIL",
    },
    "time_since_codes_cleared": {
        "mode": "01", "pid": "4E", "bytes": 2,
        "decode": lambda b: (b[0] * 256) + b[1],
        "unit": "min", "label": "Time Since Clear",
    },
    "distance_with_mil": {
        "mode": "01", "pid": "21", "bytes": 2,
        "decode": lambda b: (b[0] * 256) + b[1],
        "unit": "km", "label": "Dist w/ MIL",
    },
    "warmups_since_clear": {
        "mode": "01", "pid": "01", "bytes": 1,
        "decode": lambda b: b[0],
        "unit": "", "label": "Warmups",
    },
}
