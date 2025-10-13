"""Coordinator configuration for the tinyIoT deployment."""

# Update these paths to match the local binaries.
SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"
SIMULATOR_PATH = "/home/parks/tinyIoT/simulator/simulator.py"
PYTHON_EXEC = "python3"

# Health-check target served by the oneM2M CSE.
CSE_URL = "http://127.0.0.1:3000/tinyiot"

# Sensor Configuration
# Users can add or remove sensors here to suit their setup.
# Sensor names must not contain spaces and only lowercase.
# --sensor: "temp" | "humid" | "co2" | "soil" | etc
# --protocol: "http" | "mqtt"
# --mode: "csv" | "random"
# --frequency: seconds
# --registration: 0 | 1
SENSORS = [
    {"sensor": "temperature", "protocol": "http", "mode": "csv", "frequency": 3, "registration": 1},
    {"sensor": "humidity", "protocol": "http", "mode": "csv", "frequency": 3, "registration": 1},
    {"sensor": "co2", "protocol": "mqtt", "mode": "csv", "frequency": 3, "registration": 1},
    {"sensor": "soil", "protocol": "mqtt", "mode": "csv", "frequency": 3, "registration": 1},
]

# Headers forwarded with the health-check GET call.
HEALTHCHECK_HEADERS = {
    "X-M2M-Origin": "CAdmin",
    "X-M2M-RVI": "2a",
    "X-M2M-RI": "healthcheck",
    "Accept": "application/json",
}

# Timeout knobs expressed in seconds.
WAIT_SERVER_TIMEOUT = 30
REQUEST_TIMEOUT = 2
PROC_TERM_WAIT = 5.0
SERVER_TERM_WAIT = 5.0
JOIN_READER_TIMEOUT = 1.0
