"""PIDs Toyota Corolla XEI 2024 (Motor 2.0 Flex - 2ZR-FE).

Inclui PIDs genericos OBD-II (Mode 01) e PIDs Toyota especificos (Mode 22).
Protocolo: CAN 500kbps (ISO 15765-4). ECU: ECM 0x7E0/0x7E8.
"""

COROLLA_2024_PIDS = {
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
    "maf": {
        "mode": "01", "pid": "10", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "g/s", "label": "MAF",
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
        "unit": "%", "label": "Short Fuel Trim B1",
    },
    "fuel_trim_long_bank1": {
        "mode": "01", "pid": "07", "bytes": 1,
        "decode": lambda b: (b[0] - 128) * 100 / 128,
        "unit": "%", "label": "Long Fuel Trim B1",
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

    # ==================== MODE 22 - Toyota Especificos ====================
    # Motor ECM
    "vvt_intake_angle": {
        "mode": "22", "pid": "0110", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "°CA", "label": "VVT Intake",
    },
    "vvt_exhaust_angle": {
        "mode": "22", "pid": "0111", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "°CA", "label": "VVT Exhaust",
    },
    "knock_retard": {
        "mode": "22", "pid": "0101", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "°CA", "label": "Knock Retard",
    },
    "hpfp_duty_cycle": {
        "mode": "22", "pid": "0120", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "%", "label": "HPFP Duty",
    },
    # ABS / Chassis
    "wheel_speed_fl": {
        "mode": "22", "pid": "0141", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "km/h", "label": "Wheel FL",
    },
    "wheel_speed_fr": {
        "mode": "22", "pid": "0142", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "km/h", "label": "Wheel FR",
    },
    "wheel_speed_rl": {
        "mode": "22", "pid": "0143", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "km/h", "label": "Wheel RL",
    },
    "wheel_speed_rr": {
        "mode": "22", "pid": "0144", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "km/h", "label": "Wheel RR",
    },
    "yaw_rate": {
        "mode": "22", "pid": "0150", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "°/s", "label": "Yaw Rate",
    },
    "lateral_g": {
        "mode": "22", "pid": "0151", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "m/s²", "label": "Lateral G",
    },
    # EPS
    "steering_angle": {
        "mode": "22", "pid": "05A1", "bytes": 2,
        "decode": lambda b: ((b[0] * 256) + b[1]) / 100,
        "unit": "°", "label": "Steering Angle",
    },
}
