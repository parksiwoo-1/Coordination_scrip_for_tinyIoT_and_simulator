# Server settings
SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = "3000"
CSE_NAME = "TinyIoT"
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/{CSE_NAME}"

# Time settings
WAIT_SERVER_TIMEOUT = 30        # seconds
WAIT_PROCESS_TIMEOUT = 10       # seconds
RETRY_WAIT_SECONDS = 5          # seconds
SEND_ERROR_THRESHOLD = 5        # count
PROCESS_START_DELAY = 2         # seconds
REQUEST_TIMEOUT = 3             # socket timeout
DATA_SEND_INTERVAL = 2          # default frequency if not overridden by args

