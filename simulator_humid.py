import argparse, csv, time, requests, socket, sys, random, string
from mqtt_client import MqttOneM2MClient
import config

# ---------- Headers ----------
class Headers:
    def __init__(self, content_type=None, origin='ChumidSensor', ri='req'):
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

getHeaders = {
    'Accept': 'application/json',
    'X-M2M-Origin': 'CAdmin',
    'X-M2M-RVI': '3',
    'X-M2M-RI': 'check'
}

# ---------- Utility ----------
def request_post(url, headers, body):
    try:
        res = requests.post(url, headers=headers, json=body)
        return res.status_code == 201
    except Exception as e:
        print(f"[ERROR] Failed to send POST request: {e}")
        return False

def check_server_reachable(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=config.REQUEST_TIMEOUT):
            return True
    except:
        return False

def generate_random_value(data_type, min_val=None, max_val=None, length=None):
    if data_type == 'int':
        return str(random.randint(int(min_val), int(max_val)))
    elif data_type == 'float':
        return f"{random.uniform(min_val, max_val):.2f}"
    elif data_type == 'string':
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    else:
        return "0"

# ---------- Resource Functions ----------
def check_and_create_ae(base_url, cse, ae):
    target = f"{base_url}/{cse}/{ae}"
    try:
        if requests.get(target, headers=getHeaders).status_code == 200:
            return True
    except:
        pass
    headers = Headers(content_type='ae').headers
    body = {"m2m:ae": {"rn": ae, "api": "N.humid", "rr": True}}
    return request_post(f"{base_url}/{cse}", headers, body)

def check_and_create_cnt(base_url, cse, ae, cnt):
    target = f"{base_url}/{cse}/{ae}/{cnt}"
    try:
        if requests.get(target, headers=getHeaders).status_code == 200:
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-data')
    parser.add_argument('--Frequency', type=int, required=True)
    parser.add_argument('--Target-Server', required=True)
    parser.add_argument('--Port', required=True)
    parser.add_argument('--Registration', type=int, default=0)
    parser.add_argument('--Mode', choices=['csv', 'random'], default='csv')
    parser.add_argument('--Data-Type', choices=['int', 'float', 'string'])
    parser.add_argument('--Min', type=float)
    parser.add_argument('--Max', type=float)
    parser.add_argument('--Length', type=int)
    parser.add_argument('--Protocol', choices=['http', 'mqtt'], default='http')
    args = parser.parse_args()

    CSE, AE, CNT = config.CSE_NAME, "humidSensor", "humidity"

    if args.Protocol == 'http':
        BASE_URL = f"http://{args.Target_Server}:{args.Port}"
        print("[CHECK] Validating server and port...")
        if not check_server_reachable(args.Target_Server, args.Port):
            print(f"[ERROR] Cannot connect to server: {args.Target_Server}:{args.Port}")
            sys.exit(1)

    mqtt_client = None
    if args.Protocol == 'mqtt':
        mqtt_client = MqttOneM2MClient(args.Target_Server, args.Port, "ChumidSensor", CSE)
        if not mqtt_client.connect():
            sys.exit(1)

    if args.Registration == 1:
        print("[HUMID] Registering AE and CNT...")
        if args.Protocol == 'http':
            check_and_create_ae(BASE_URL, CSE, AE)
            check_and_create_cnt(BASE_URL, CSE, AE, CNT)
        else:
            mqtt_client.create_ae(AE)
            mqtt_client.create_cnt(AE, CNT)

    data = []
    if args.Mode == 'csv':
        try:
            with open(args.input_data, 'r') as file:
                reader = list(csv.reader(file))
                data = [row[0].strip() for row in reader if row]
        except Exception as e:
            print(f"[ERROR] Failed to open CSV file: {e}")
            sys.exit(1)
        if not data:
            print("[ERROR] CSV data is empty.")
            sys.exit(1)

    print("[HUMID] Starting data transmission...")
    index = 0
    error_count = 0

    while True:
        value = data[index] if args.Mode == 'csv' else generate_random_value(args.Data_Type, args.Min, args.Max, args.Length)

        if args.Protocol == 'http':
            success = send_cin(BASE_URL, CSE, AE, CNT, value)
        else:
            success = mqtt_client.send_cin(AE, CNT, value)

        if success:
            print(f"[HUMID] Successfully sent: {value}")
            index += 1 if args.Mode == 'csv' else 0
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
