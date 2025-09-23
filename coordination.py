import os
import subprocess
import sys
import time
import requests
import config_coord as config

def wait_for_server(timeout=getattr(config, 'WAIT_SERVER_TIMEOUT', 30)):
    print("[COORD] Waiting for server response...")
    headers = {'X-M2M-Origin': 'CAdmin', 'X-M2M-RVI': '3', 'X-M2M-RI': 'healthcheck'}
    url = f"{config.CSE_URL}"
    req_timeout = getattr(config, 'REQUEST_TIMEOUT', 2)
    
    for i in range(timeout):
        try:
            res = requests.get(url, headers=headers, timeout=req_timeout)
            if res.status_code == 200:
                print("[COORD] tinyIoT server is responsive.")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    print("[ERROR] Unable to connect to tinyIoT server.")
    return False

def wait_for_process(name, timeout=getattr(config, 'WAIT_PROCESS_TIMEOUT', 30)):
    print(f"[COORD] Checking process: {name}...")
    for i in range(timeout):
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

class SensorConfig:
    def __init__(self, sensor_type, protocol='mqtt', mode='random', frequency=2, registration=1):
        self.sensor_type = sensor_type
        self.protocol = protocol
        self.mode = mode
        self.frequency = frequency
        self.registration = registration

SENSORS_TO_RUN = [
    SensorConfig('temp', protocol='mqtt', mode='random', frequency=3, registration=1),
    SensorConfig('humid', protocol='mqtt', mode='random', frequency=3, registration=1),
    SensorConfig('co2', protocol='mqtt', mode='random', frequency=3, registration=1),
    SensorConfig('soil', protocol='mqtt', mode='random', frequency=3, registration=1)
    # 더 많은 센서 추가 예시:
    # SensorConfig('temp', protocol='http', mode='csv', frequency=1, registration=1),
    # SensorConfig('humid', protocol='http', mode='random', frequency=5, registration=1),
    # SensorConfig('temp', protocol='mqtt', mode='random', frequency=10, registration=1),
]

def launch_simulator(sensor_config, index):
    python_exec = getattr(config, 'PYTHON_EXEC', 'python3')
    simulator_path = config.SIMULATOR_PATH
    
    sim_args = [
        python_exec, simulator_path,
        '--sensor', sensor_config.sensor_type,
        '--protocol', sensor_config.protocol,
        '--mode', sensor_config.mode,
        '--frequency', str(sensor_config.frequency),
        '--registration', str(sensor_config.registration),
    ]
    
    print(f"[COORD] Starting simulator #{index+1} ({sensor_config.sensor_type} sensor)...")
    print(f"[COORD] Command: {' '.join(sim_args)}")
    
    try:
        proc = subprocess.Popen(sim_args)
        return proc
    except Exception as e:
        print(f"[ERROR] Failed to start simulator #{index+1}: {e}")
        return None

if __name__ == '__main__':
    print("[COORD] Starting tinyIoT server...")
    server_proc = subprocess.Popen([config.SERVER_EXEC])
    
    if not wait_for_server():
        try:
            server_proc.terminate()
        except Exception:
            pass
        sys.exit(1)
    
    simulator_procs = []
    sim_name = os.path.basename(config.SIMULATOR_PATH)
    
    print(f"\n[COORD] Launching {len(SENSORS_TO_RUN)} sensor simulators...")
    
    for i, sensor_config in enumerate(SENSORS_TO_RUN):
        proc = launch_simulator(sensor_config, i)
        if proc:
            simulator_procs.append(proc)
            time.sleep(0.5)
        else:
            print(f"[ERROR] Failed to launch simulator #{i+1}")
    
    if not simulator_procs:
        print("[ERROR] No simulators were started successfully.")
        try:
            server_proc.terminate()
        except Exception:
            pass
        sys.exit(1)
    
    print(f"\n[COORD] Successfully started {len(simulator_procs)} simulator(s).")
    print("[COORD] Press Ctrl+C to stop all processes.\n")
    
    try:
        while True:
            if server_proc.poll() is not None:
                print("[ERROR] tinyIoT server has stopped unexpectedly.")
                break
            
            running_sims = sum(1 for p in simulator_procs if p.poll() is None)
            if running_sims == 0:
                print("[COORD] All simulators have stopped.")
                break
            
            time.sleep(5)  
            
    except KeyboardInterrupt:
        print("\n[COORD] Shutting down (KeyboardInterrupt)...")
    
    finally:
        print("[COORD] Terminating all processes...")
        
        for i, proc in enumerate(simulator_procs):
            if proc and proc.poll() is None:
                try:
                    print(f"[COORD] Terminating simulator #{i+1}...")
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception as e:
                    print(f"[ERROR] Failed to terminate simulator #{i+1}: {e}")
                    try:
                        proc.kill()
                    except Exception:
                        pass
        
        if server_proc and server_proc.poll() is None:
            try:
                print("[COORD] Terminating tinyIoT server...")
                server_proc.terminate()
                server_proc.wait(timeout=5)
            except Exception as e:
                print(f"[ERROR] Failed to terminate server: {e}")
                try:
                    server_proc.kill()
                except Exception:
                    pass
        
        print("[COORD] All processes terminated.")
