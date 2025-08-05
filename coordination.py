import subprocess
import time
import requests

SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"
SERVER_URL = "http://127.0.0.1:3000/TinyIoT"

def wait_for_server(timeout=30):
    print("[COORD] Waiting for server response...")
    headers = {
        'X-M2M-Origin': 'CAdmin',
        'X-M2M-RVI': '3',
        'X-M2M-RI': 'healthcheck'
    }
    for _ in range(timeout):
        try:
            res = requests.get(SERVER_URL, headers=headers)
            if res.status_code == 200:
                print("[COORD] tinyIoT server is responsive.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("[ERROR] Unable to connect to tinyIoT server.")
    return False

def wait_for_process(name, timeout=10):
    print(f"[COORD] Checking process: {name}...")
    for _ in range(timeout):
        try:
            out = subprocess.check_output(['pgrep', '-f', name])
            if out:
                print(f"[COORD] {name} is running.")
                return True
        except subprocess.CalledProcessError:
            pass
        time.sleep(1)
    print(f"[ERROR] Failed to detect running process: {name}.")
    return False

if __name__ == '__main__':
    server_proc = subprocess.Popen([SERVER_EXEC])
    time.sleep(2)

    if not wait_for_server():
        server_proc.terminate()
        exit(1)

    print("[COORD] Starting simulator_temp...")
    device1 = subprocess.Popen([
        'python3', 'devices/simulator_temp.py',
        '--Mode', 'random',
        '--Data-Type', 'float',
        '--Min', '20.0', '--Max', '35.0',
        '--Frequency', '2',
        '--Target-Server', '127.0.0.1',
        '--Port', '3000',
        '--Registration', '1',
        '--Protocol', 'mqtt'
    ])

    if not wait_for_process("simulator_temp.py"):
        print("[ERROR] Failed to start device1. Exiting.")
        device1.terminate()
        server_proc.terminate()
        exit(1)

    print("[COORD] Starting simulator_humid...")
    device2 = subprocess.Popen([
        'python3', 'devices/simulator_humid.py',
        '--Mode', 'random',
        '--Data-Type', 'int',
        '--Min', '50', '--Max', '90',
        '--Frequency', '2',
        '--Target-Server', '127.0.0.1',
        '--Port', '3000',
        '--Registration', '1',
        '--Protocol', 'mqtt'
    ])

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        device1.terminate()
        device2.terminate()
        server_proc.terminate()
