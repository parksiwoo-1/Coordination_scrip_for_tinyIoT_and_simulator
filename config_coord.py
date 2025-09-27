"""Configuration for the coordinator script and child device simulators."""

# -------------------------- Paths --------------------------
# configure for your environment
SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"
SIMULATOR_PATH = "/home/parks/tinyIoT/simulator/simulator.py"
PYTHON_EXEC = "python3"

# -------------------- Health Check URL --------------------
# OneM2M CSE HTTP endpoint used for server readiness checks.
# configure for your environment
CSE_URL = "http://127.0.0.1:3000/tinyiot"

# ---------------- Timeouts & Retries ----------------
WAIT_SERVER_TIMEOUT = 30   # seconds
REQUEST_TIMEOUT = 2        # seconds

# Cleanup timings used when a simulator or the server fails to shut down promptly.
PROC_TERM_WAIT = 5.0       # seconds
SERVER_TERM_WAIT = 5.0     # seconds
JOIN_READER_TIMEOUT = 1.0  # seconds
