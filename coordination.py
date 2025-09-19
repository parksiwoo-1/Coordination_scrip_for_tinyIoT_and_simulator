import os
import subprocess
import sys
import requests
import config_coord as config

def wait_for_server(timeout=getattr(config, 'WAIT_SERVER_TIMEOUT', 30)):
    print("[COORD] Waiting for server response...")
    headers = {'X-M2M-Origin': 'CAdmin', 'X-M2M-RVI': '3', 'X-M2M-RI': 'healthcheck'}
    url = f"{config.CSE_URL}"
    req_timeout = getattr(config, 'REQUEST_TIMEOUT', 2)

    for _ in range(timeout):
        try:
            res = requests.get(url, headers=headers, timeout=req_timeout)
            if res.status_code == 200:
                print("[COORD] tinyIoT server is responsive.")
                return True
        except requests.exceptions.RequestException:
            pass
    print("[ERROR] Unable to connect to tinyIoT server.")
    return False

def wait_for_process(name, timeout=getattr(config, 'WAIT_PROCESS_TIMEOUT', 30)):
    print(f"[COORD] Checking process: {name}...")
    for _ in range(timeout):
        try:
            out = subprocess.check_output(['pgrep', '-f', name])
            if out:
                print(f"[COORD] {name} is running.")
                return True
        except subprocess.CalledProcessError:
            pass
    print(f"[ERROR] Failed to detect running process: {name}.")
    return False

if __name__ == '__main__':
    print("[COORD] Starting tinyIoT server...")
    server_proc = subprocess.Popen([config.SERVER_EXEC])

    if not wait_for_server():
        try: server_proc.terminate()
        except Exception: pass
        sys.exit(1)

    PROTOCOL_1     = 'mqtt'
    MODE_1         = 'random'
    FREQUENCY_1    = 2
    REGISTRATION_1 = 1

    PROTOCOL_2     = 'mqtt'
    MODE_2         = 'random'
    FREQUENCY_2    = 2
    REGISTRATION_2 = 1

    python_exec = getattr(config, 'PYTHON_EXEC', 'python3')
    simulator_path = config.SIMULATOR_PATH

    sim_args = [
        python_exec, simulator_path,
        '--sensor', 'temp',
        '--protocol', PROTOCOL_1,
        '--mode', MODE_1,
        '--frequency', str(FREQUENCY_1),
        '--registration', str(REGISTRATION_1),
        '--sensor', 'humid',
        '--protocol', PROTOCOL_2,
        '--mode', MODE_2,
        '--frequency', str(FREQUENCY_2),
        '--registration', str(REGISTRATION_2),
    ]

    print("[COORD] Starting simulator (single process)...")
    sim_proc = subprocess.Popen(sim_args)
    sim_name = os.path.basename(simulator_path)
    if not wait_for_process(sim_name):
        print("[ERROR] Failed to start simulator. Exiting.")
        try: sim_proc.terminate()
        except Exception: pass
        try: server_proc.terminate()
        except Exception: pass
        sys.exit(1)

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[COORD] Shutting down (KeyboardInterrupt)...")
    finally:
        for p in (sim_proc,):
            try: p.terminate()
            except Exception: pass
        try: server_proc.terminate()
        except Exception: pass
