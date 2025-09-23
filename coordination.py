import subprocess
import sys
import time
import requests
import logging
import config_coord as config
from typing import List, Optional

logging.basicConfig(level=getattr(config, 'LOG_LEVEL', logging.INFO), format='[%(levelname)s] %(message)s')

def wait_for_server(timeout: int = getattr(config, 'WAIT_SERVER_TIMEOUT', 30)) -> bool:
    headers = {'X-M2M-Origin': 'CAdmin', 'X-M2M-RVI': '3', 'X-M2M-RI': 'healthcheck'}
    url = f"{config.CSE_URL}"
    req_timeout = getattr(config, 'REQUEST_TIMEOUT', 2)
    for _ in range(timeout):
        try:
            res = requests.get(url, headers=headers, timeout=req_timeout)
            if res.status_code == 200:
                logging.info("[COORD] tinyIoT server is responsive.")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    logging.error("[COORD] Unable to connect to tinyIoT server.")
    return False

def wait_for_process(name: str, timeout: int = getattr(config, 'WAIT_PROCESS_TIMEOUT', 30)) -> bool:
    logging.info(f"[COORD] Checking process: {name}...")
    for _ in range(timeout):
        try:
            out = subprocess.check_output(['pgrep', '-f', name])
            if out:
                logging.info(f"[COORD] {name} is running.")
                return True
        except subprocess.CalledProcessError:
            pass
        time.sleep(1)
    logging.error(f"[COORD] Failed to detect running process: {name}.")
    return False

class SensorConfig:
    def __init__(self, sensor_type: str, protocol: str = 'mqtt', mode: str = 'random',
                 frequency: int = 2, registration: int = 1) -> None:
        self.sensor_type = sensor_type
        self.protocol = protocol
        self.mode = mode
        self.frequency = frequency
        self.registration = registration

SENSORS_TO_RUN: List[SensorConfig] = [
    SensorConfig('temp',  protocol='http', mode='random', frequency=3, registration=1),
    SensorConfig('humid', protocol='http', mode='random', frequency=3, registration=1),
    SensorConfig('co2',   protocol='mqtt', mode='random', frequency=3, registration=1),
    SensorConfig('soil',  protocol='mqtt', mode='random', frequency=3, registration=1),
]

def launch_simulator(sensor_config: SensorConfig, index: int) -> Optional[subprocess.Popen]:
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
    logging.info(f"[COORD] Starting simulator #{index + 1} ({sensor_config.sensor_type} sensor)...")
    logging.debug(f"[COORD] Command: {' '.join(sim_args)}")
    try:
        proc = subprocess.Popen(sim_args)
        return proc
    except Exception as e:
        logging.error(f"[COORD] Failed to start simulator #{index + 1}: {e}")
        return None

if __name__ == '__main__':
    logging.info("[COORD] Starting tinyIoT server...")
    try:
        server_proc = subprocess.Popen([config.SERVER_EXEC])
    except Exception as e:
        logging.error(f"[COORD] Failed to start tinyIoT server: {e}")
        sys.exit(1)

    if not wait_for_server():
        try:
            server_proc.terminate()
        except Exception:
            pass
        sys.exit(1)

    simulator_procs: List[subprocess.Popen] = []
    logging.info(f"[COORD] Launching {len(SENSORS_TO_RUN)} sensor simulators...")

    for i, sensor_conf in enumerate(SENSORS_TO_RUN):
        proc = launch_simulator(sensor_conf, i)
        if proc:
            simulator_procs.append(proc)
            time.sleep(0.5)
        else:
            logging.error(f"[COORD] Failed to launch simulator #{i + 1}")

    if not simulator_procs:
        logging.error("[COORD] No simulators were started successfully.")
        try:
            server_proc.terminate()
        except Exception:
            pass
        sys.exit(1)

    logging.info(f"[COORD] Successfully started {len(simulator_procs)} simulator(s).")
    logging.info("[COORD] Press Ctrl+C to stop all processes.")

    try:
        while True:
            if server_proc.poll() is not None:
                logging.error("[COORD] tinyIoT server has stopped unexpectedly.")
                break
            running_sims = sum(1 for p in simulator_procs if p.poll() is None)
            if running_sims == 0:
                logging.info("[COORD] All simulators have stopped.")
                break
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("[COORD] Shutting down (KeyboardInterrupt)...")
    finally:
        logging.info("[COORD] Terminating all processes...")
        for i, proc in enumerate(simulator_procs):
            if proc and proc.poll() is None:
                try:
                    logging.info(f"[COORD] Terminating simulator #{i + 1}...")
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception as e:
                    logging.warning(f"[COORD] Failed to terminate simulator #{i + 1}: {e}; killing...")
                    try:
                        proc.kill()
                    except Exception:
                        pass
        if server_proc and server_proc.poll() is None:
            try:
                logging.info("[COORD] Terminating tinyIoT server...")
                server_proc.terminate()
                server_proc.wait(timeout=5)
            except Exception as e:
                logging.warning(f"[COORD] Failed to terminate server: {e}; killing...")
                try:
                    server_proc.kill()
                except Exception:
                    pass
        logging.info("[COORD] All processes terminated.")
