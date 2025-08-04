import subprocess
import time
import requests

# tinyIoT 서버 실행 경로
SERVER_EXEC = "/home/parks/tinyIoT/source/server/server"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = "443"  # HTTPS 포트
USE_HTTPS = True
VERIFY_CERT = False
PROTOCOL = "https" if USE_HTTPS else "http"
SERVER_URL = f"{PROTOCOL}://{SERVER_HOST}:{SERVER_PORT}/TinyIoT"


def wait_for_server(timeout=30):
    print("[COORD] 서버가 켜질 때까지 대기 중...")
    headers = {
        'X-M2M-Origin': 'CAdmin',
        'X-M2M-RVI': '3',
        'X-M2M-RI': 'healthcheck'
    }
    for _ in range(timeout):
        try:
            res = requests.get(SERVER_URL, headers=headers, verify=VERIFY_CERT)
            if res.status_code == 200:
                print("[COORD] tinyIoT 서버 응답 확인 완료.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("[ERROR] tinyIoT 서버에 연결할 수 없습니다.")
    return False


def wait_for_process(name, timeout=10):
    print(f"[COORD] {name} 프로세스 확인 중...")
    for _ in range(timeout):
        try:
            out = subprocess.check_output(['pgrep', '-f', name])
            if out:
                print(f"[COORD] {name} 실행 확인됨.")
                return True
        except subprocess.CalledProcessError:
            pass
        time.sleep(1)
    print(f"[ERROR] {name} 실행 확인 실패.")
    return False


if __name__ == '__main__':
    server_proc = subprocess.Popen([SERVER_EXEC])
    time.sleep(2)

    if not wait_for_server():
        server_proc.terminate()
        exit(1)

    print("[COORD] simulator_temp 실행")
    device1 = subprocess.Popen([
        'python3', 'devices/simulator_temp.py',
        '--input-data', 'script/test_data/test_data_temp.csv',
        '--Frequency', '2',
        '--Target-Server', SERVER_HOST,
        '--Port', SERVER_PORT,
        '--Registration', '1',
        '--Use-HTTPS', '1',
        '--Verify-Cert', '0'
    ])

    if not wait_for_process("simulator_temp.py"):
        print("[ERROR] device1 실행 실패. 종료합니다.")
        device1.terminate()
        server_proc.terminate()
        exit(1)

    print("[COORD] simulator_humid 실행")
    device2 = subprocess.Popen([
        'python3', 'devices/simulator_humid.py',
        '--input-data', 'script/test_data/test_data_humid.csv',
        '--Frequency', '2',
        '--Target-Server', SERVER_HOST,
        '--Port', SERVER_PORT,
        '--Registration', '1',
        '--Use-HTTPS', '1',
        '--Verify-Cert', '0'
    ])

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        device1.terminate()
        device2.terminate()
        server_proc.terminate()