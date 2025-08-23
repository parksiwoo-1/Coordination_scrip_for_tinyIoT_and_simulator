import argparse, csv, time, requests, socket, sys, random, string
from mqtt_client import MqttOneM2MClient
import config

# ---------- Headers ----------
class Headers:
    def __init__(self, content_type=None, origin='CtempSensor', ri='req'):
        self.headers = {
            'Accept': 'application/json',
            'X-M2M-Origin': origin,
            'X-M2M-RVI': '3',
            'X-M2M-RI': ri,
            'Content-Type': f'application/json;ty={self.get_content_type(content_type)}' if content_type else 'application/json'
        }
    @staticmethod
    def get_content_type(content_type):
        return {'ae': 2, 'cnt': 3, 'cin': 4}.get(content_type)

GET_HEADERS = {
    'Accept': 'application/json',
    'X-M2M-Origin': 'CAdmin',
    'X-M2M-RVI': '3',
    'X-M2M-RI': 'check'
}

# ---------- Utility ----------
def request_post(url, headers, body):
    try:
        res = requests.post(url, headers=headers, json=body, timeout=config.REQUEST_TIMEOUT)
        return res.status_code == 201
    except Exception as e:
        print(f"[ERROR] Failed to send POST request: {e}")
        return False

def check_http_reachable():
    try:
        with socket.create_connection((config.HTTP_HOST, int(config.HTTP_PORT)), timeout=config.REQUEST_TIMEOUT):
            return True
    except:
        return False

def generate_random_value_from_profile(profile):
    dt = profile['data_type']
    if dt == 'int':
        return str(random.randint(int(profile['min']), int(profile['max'])))
    if dt == 'float':
        return f"{random.uniform(float(profile['min']), float(profile['max'])):.2f}"
    if dt == 'string':
        length = int(profile.get('length') or 8)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return "0"

# ---------- Resource Functions ----------
def check_and_create_ae(base_url, cse, ae):
    target = f"{base_url}/{cse}/{ae}"
    try:
        if requests.get(target, headers=GET_HEADERS, timeout=config.REQUEST_TIMEOUT).status_code == 200:
            return True
    except:
        pass
    headers = Headers(content_type='ae').headers
    body = {"m2m:ae": {"rn": ae, "api": "N.temp", "rr": True}}
    return request_post(f"{base_url}/{cse}", headers, body)

def check_and_create_cnt(base_url, cse, ae, cnt):
    target = f"{base_url}/{cse}/{ae}/{cnt}"
    try:
        if requests.get(target, headers=GET_HEADERS, timeout=config.REQUEST_TIMEOUT).status_code == 200:
            return True
    except:
        pass
    headers = Headers(content_type='cnt').headers
    body = {"m2m:cnt": {"rn": cnt}}
    return request_post(f"{base_url}/{cse}/{ae}", headers, body)

def send_cin(base_url, cse, ae, cnt, value):
    headers = Headers(content_type='cin').headers
    body = {"m2m:cin": {"con": value}}
    return request_post(f"{base_url}/{cse}/{ae}/{cnt}", headers, body)

# ---------- Main ----------
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--Frequency', type=int, required=True)
    p.add_argument('--Registration', type=int, default=0)
    p.add_argument('--Mode', choices=['csv', 'random'], default='csv')
    p.add_argument('--Protocol', choices=['http', 'mqtt'], default='http')
    args = p.parse_args()

    CSE, AE, CNT = config.CSE_NAME, "tempSensor", "temperature"

    # 프로토콜별 대상은 전부 config에서
    base_url = f"http://{config.HTTP_HOST}:{config.HTTP_PORT}"
    mqtt_client = None

    if args.Protocol == 'http':
        print("[CHECK] Validating HTTP server/port from config...")
        if not check_http_reachable():
            print(f"[ERROR] Cannot connect to HTTP server: {config.HTTP_HOST}:{config.HTTP_PORT}")
            sys.exit(1)
    else:
        mqtt_client = MqttOneM2MClient(config.MQTT_HOST, config.MQTT_PORT, "CtempSensor", CSE)
        if not mqtt_client.connect():
            sys.exit(1)

    # Registration (AE/CNT)
    if args.Registration == 1:
        print("[TEMP] Registering AE and CNT...")
        if args.Protocol == 'http':
            check_and_create_ae(base_url, CSE, AE)
            check_and_create_cnt(base_url, CSE, AE, CNT)
        else:
            mqtt_client.create_ae(AE)
            mqtt_client.create_cnt(AE, CNT)

    # 데이터 소스 준비
    data = []
    if args.Mode == 'csv':
        path = config.TEMP_CSV
        try:
            with open(path, 'r') as f:
                reader = list(csv.reader(f))
                data = [row[0].strip() for row in reader if row]
        except Exception as e:
            print(f"[ERROR] Failed to open CSV file: {e}")
            sys.exit(1)
        if not data:
            print("[ERROR] CSV data is empty.")
            sys.exit(1)

    print("[TEMP] Starting data transmission...")
    index = 0
    error_count = 0

    while True:
        if args.Mode == 'csv':
            value = data[index]
        else:
            value = generate_random_value_from_profile(config.TEMP_PROFILE)

        # 전송
        success = (
            send_cin(base_url, CSE, AE, CNT, value)
            if args.Protocol == 'http'
            else mqtt_client.send_cin(AE, CNT, value)
        )

        if success:
            print(f"[TEMP] Successfully sent: {value}")
            if args.Mode == 'csv':
                index += 1
            error_count = 0
        else:
            error_count += 1
            print(f"[ERROR] Failed to send: {value} (Retrying in {config.RETRY_WAIT_SECONDS} sec)")
            time.sleep(config.RETRY_WAIT_SECONDS)
            if error_count >= config.SEND_ERROR_THRESHOLD:
                print("[ERROR] Repeated failures detected. Exiting.")
                break

        if args.Mode == 'csv' and index >= len(data):
            print("[INFO] All data has been sent. Exiting.")
            break

        time.sleep(args.Frequency)

    if mqtt_client:
        mqtt_client.disconnect()
