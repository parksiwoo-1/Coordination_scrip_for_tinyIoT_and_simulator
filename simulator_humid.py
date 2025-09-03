import argparse
import config
import csv
import random
import requests
import socket
import string
import sys
import time
from mqtt_client import MqttOneM2MClient

# ---- Timeouts/Jitter (fallback if not in config) ----
CONNECT_TIMEOUT = getattr(config, 'CONNECT_TIMEOUT', 2)
READ_TIMEOUT    = getattr(config, 'READ_TIMEOUT', 10)
JITTER_MAX      = getattr(config, 'JITTER_MAX', 0.3)
CNT_MNI         = getattr(config, 'CNT_MNI', 1000)
CNT_MBS         = getattr(config, 'CNT_MBS', 10485760)

HTTP = requests.Session()

# ---------- Headers ----------
class Headers:
    def __init__(self, content_type=None, origin='CAdmin', ri='req'):
        self.headers = {
            'Accept': 'application/json',
            'X-M2M-Origin': origin,
            'X-M2M-RVI': '2a',
            'X-M2M-RI': ri,
            'Content-Type': 'application/json'
        }
        if content_type:
            self.headers['Content-Type'] = f'application/json;ty={self.get_content_type(content_type)}'

    @staticmethod
    def get_content_type(content_type):
        return {'ae': 2, 'cnt': 3, 'cin': 4}.get(content_type)

GET_HEADERS = {
    'Accept': 'application/json',
    'X-M2M-Origin': 'CAdmin',
    'X-M2M-RVI': '2a',
    'X-M2M-RI': 'check'
}

# ---------- URLs (Hierarchical: RN) ----------
BASE_URL_RN = f"http://{config.HTTP_HOST}:{config.HTTP_PORT}/{config.CSE_RN}"
def url_ae(ae):          return f"{BASE_URL_RN}/{ae}"
def url_cnt(ae, cnt):    return f"{BASE_URL_RN}/{ae}/{cnt}"

# ---------- Utility ----------
def http_get_ok(url):
    try:
        r = HTTP.get(url, headers=GET_HEADERS, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        return r.status_code == 200
    except Exception:
        return False

def request_post(url, headers, body, kind=""):
    try:
        r = HTTP.post(url, headers=headers, json=body, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        if r.status_code in (200, 201):
            return True
        try: text = r.json()
        except Exception: text = r.text
        if r.status_code in (403, 409) and "duplicat" in str(text).lower():
            return True
        print(f"[ERROR] POST {url} -> {r.status_code} {text}")
        return False
    except requests.exceptions.ReadTimeout as e:
        print(f"[WARN] POST timeout on {url}: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] POST {url} failed: {e}")
        return False

def check_http_reachable():
    try:
        with socket.create_connection((config.HTTP_HOST, int(config.HTTP_PORT)), timeout=CONNECT_TIMEOUT):
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

# ---------- oneM2M Helpers ----------
def check_and_create_ae(ae):
    if http_get_ok(url_ae(ae)):
        return True
    hdr  = Headers(content_type='ae').headers
    body = {"m2m:ae": {"rn": ae, "api": "N.humid", "rr": True}}
    return request_post(BASE_URL_RN, hdr, body, "ae")

def check_and_create_cnt(ae, cnt):
    if http_get_ok(url_cnt(ae, cnt)):
        return True
    hdr  = Headers(content_type='cnt').headers
    body = {"m2m:cnt": {"rn": cnt, "mni": CNT_MNI, "mbs": CNT_MBS}}
    return request_post(url_ae(ae), hdr, body, "cnt")

def get_latest_con(ae, cnt):
    la = f"{url_cnt(ae, cnt)}/la"
    try:
        r = HTTP.get(la, headers=GET_HEADERS, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        if r.status_code == 200:
            js = r.json()
            return js.get('m2m:cin', {}).get('con')
    except Exception:
        pass
    return None

def send_cin_http(ae, cnt, value):
    hdr  = Headers(content_type='cin').headers
    body = {"m2m:cin": {"con": value}}
    u    = url_cnt(ae, cnt)
    try:
        r = HTTP.post(u, headers=hdr, json=body, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        if r.status_code in (200, 201):
            return True
        try: text = r.json()
        except Exception: text = r.text
        print(f"[ERROR] POST {u} -> {r.status_code} {text}")
        return False
    except requests.exceptions.ReadTimeout:
        latest = get_latest_con(ae, cnt)
        if latest == str(value):
            print("[WARN] POST timed out but verified via /la (stored).")
            return True
        print("[WARN] POST timed out and not verified; will retry.")
        return False
    except Exception as e:
        print(f"[ERROR] POST {u} failed: {e}")
        return False

# ---------- Main ----------
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--protocol', choices=['http', 'mqtt'], default='http')
    p.add_argument('--mode', choices=['csv', 'random'], default='csv')
    p.add_argument('--frequency', type=int, required=True)
    p.add_argument('--registration', type=int, default=0)
    args = p.parse_args()

    AE, CNT = "ChumidSensor", "humidity"
    mqtt = None

    if args.protocol == 'http':
        print("[CHECK] Validating HTTP server/port from config...")
        if not check_http_reachable():
            print(f"[ERROR] Cannot connect to HTTP server: {config.HTTP_HOST}:{config.HTTP_PORT}")
            sys.exit(1)
    else:
        mqtt = MqttOneM2MClient(
            config.MQTT_HOST, config.MQTT_PORT,
            origin="ChumidSensor",
            cse_csi=config.CSE_NAME,
            cse_rn=config.CSE_RN
        )
        if not mqtt.connect():
            sys.exit(1)

    if args.registration == 1:
        print("[HUMID] Registering AE and CNT...")
        if args.protocol == 'http':
            if not check_and_create_ae(AE):
                print("[ERROR] AE creation failed.")
                sys.exit(1)
            time.sleep(0.2)
            if not check_and_create_cnt(AE, CNT):
                print("[ERROR] CNT creation failed.")
                sys.exit(1)
            time.sleep(0.2)
        else:
            if not mqtt.create_ae(AE):  sys.exit(1)
            if not mqtt.create_cnt(AE, CNT): sys.exit(1)

    data = []
    if args.mode == 'csv':
        path = config.HUMID_CSV
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

    print("[HUMID] Starting data transmission...")
    index = 0
    error_count = 0

    while True:
        value = data[index] if args.mode == 'csv' else generate_random_value_from_profile(config.HUMID_PROFILE)
        ok = send_cin_http(AE, CNT, value) if args.protocol=='http' else mqtt.send_cin(AE, CNT, value)

        if ok:
            print(f"[HUMID] Successfully sent: {value}")
            if args.mode == 'csv':
                index += 1
            error_count = 0
        else:
            error_count += 1
            print(f"[ERROR] Failed to send: {value} (Retrying in {config.RETRY_WAIT_SECONDS} sec)")
            time.sleep(config.RETRY_WAIT_SECONDS)
            if error_count >= config.SEND_ERROR_THRESHOLD:
                print("[ERROR] Repeated failures detected. Exiting.")
                break

        if args.mode == 'csv' and index >= len(data):
            print("[INFO] All data has been sent. Exiting.")
            break

        time.sleep(args.frequency + random.uniform(0, JITTER_MAX))

    if mqtt:
        mqtt.disconnect()

if __name__ == '__main__':
    main()
