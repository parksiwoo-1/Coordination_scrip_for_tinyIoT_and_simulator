import subprocess
import sys
import time
import requests
import config

def wait_for_server(timeout=config.WAIT_SERVER_TIMEOUT):
    print("[COORD] Waiting for server response...")
    headers = {'X-M2M-Origin': 'CAdmin', 'X-M2M-RVI': '3', 'X-M2M-RI': 'healthcheck'}
    url = f"{config.CSE_URL}"
    for _ in range(timeout):
        try:
            res = requests.get(url, headers=headers, timeout=2)
            if res.status_code == 200:
                print("[COORD] tinyIoT server is responsive.")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    print("[ERROR] Unable to connect to tinyIoT server.")
    return False

def wait_for_process(name, timeout=config.WAIT_PROCESS_TIMEOUT):
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
    print("[COORD] Starting tinyIoT server...")
    server_proc = subprocess.Popen([config.SERVER_EXEC])
    time.sleep(config.PROCESS_START_DELAY)

    if not wait_for_server():
        try: server_proc.terminate()
        except Exception: pass
        sys.exit(1)

    PROTOCOL_1     = 'mqtt'
    MODE_1         = 'random'
    FREQUENCY_1    = 2   # seconds
    REGISTRATION_1 = 1

    PROTOCOL_2     = 'mqtt'
    MODE_2         = 'random'
    FREQUENCY_2    = 2   # seconds
    REGISTRATION_2 = 1

    print("[COORD] Starting simulator_temp...")
    device1 = subprocess.Popen([
        'python3', 'simulator_temp.py',
        '--Protocol', PROTOCOL_1,
        '--Mode', MODE_1,
        '--Frequency', str(FREQUENCY_1),
        '--Registration', str(REGISTRATION_1),
    ])

    if not wait_for_process("simulator_temp.py"):
        print("[ERROR] Failed to start simulator_temp. Exiting.")
        try: device1.terminate()
        except Exception: pass
        try: server_proc.terminate()
        except Exception: pass
        sys.exit(1)

    print("[COORD] Starting simulator_humid...")
    device2 = subprocess.Popen([
        'python3', 'simulator_humid.py',
        '--Protocol', PROTOCOL_2,
        '--Mode', MODE_2,
        '--Frequency', str(FREQUENCY_2),
        '--Registration', str(REGISTRATION_2),
    ])

    if not wait_for_process("simulator_humid.py"):
        print("[ERROR] Failed to start simulator_humid. Exiting.")
        try: device2.terminate()
        except Exception: pass
        try: device1.terminate()
        except Exception: pass
        try: server_proc.terminate()
        except Exception: pass
        sys.exit(1)

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[COORD] Shutting down (KeyboardInterrupt)...")
    finally:
        for p in (device1, device2):
            try: p.terminate()
            except Exception: pass
        try: server_proc.terminate()
        except Exception: pass
