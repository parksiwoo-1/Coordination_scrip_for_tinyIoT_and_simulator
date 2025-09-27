"""Configuration values for the coordination launcher and child device simulators."""

# ----------------------- Paths -----------------------
SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"
SIMULATOR_PATH = "/home/parks/tinyIoT/simulator/simulator.py"
PYTHON_EXEC = "python3"

# ------------------- Health Check URL -------------------
# OneM2M CSE HTTP endpoint used for server readiness checks.
# NOTE: CSI is lowercase ("tinyiot"). Change only if your CSE path differs.
CSE_URL = "http://127.0.0.1:3000/tinyiot"

# ---------------- Timeouts & Retries ----------------
WAIT_SERVER_TIMEOUT = 30  # seconds
WAIT_PROCESS_TIMEOUT = 10  # seconds
REQUEST_TIMEOUT = 2  # seconds
