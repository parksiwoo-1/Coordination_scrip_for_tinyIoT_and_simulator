# Server/TinyIoT
SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"

# oneM2M CSE
CSE_NAME = "tinyiot"   # csi (use topic)
CSE_RN   = "TinyIoT"   # rn  (use MQTT payload "to")

# HTTP (REST)
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 3000  
HTTP_BASE = f"http://{HTTP_HOST}:{HTTP_PORT}"
CSE_URL = f"{HTTP_BASE}/{CSE_NAME}"

# MQTT (Mosquitto)
MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883  # int

# Time & Retry
WAIT_SERVER_TIMEOUT   = 30  # seconds
WAIT_PROCESS_TIMEOUT  = 10  # seconds
RETRY_WAIT_SECONDS    = 5   # seconds
SEND_ERROR_THRESHOLD  = 5   # count
PROCESS_START_DELAY   = 2   # seconds
REQUEST_TIMEOUT       = 3   # seconds

# CSV Paths
TEMP_CSV  = "test data/test_data_temp.csv"
HUMID_CSV = "test data/test_data_humid.csv"

# ---------- Device Profiles (used in random mode) ----------
TEMP_PROFILE = {
    "data_type": "float",   # int | float
    "min": 20.0,
    "max": 35.0,
}

HUMID_PROFILE = {
    "data_type": "float",     # int | float
    "min": 50,
    "max": 90,
}
