import argparse
import csv
import time
import requests
import socket
import sys

# ----------- oneM2M Basic Settings ----------- 
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

# ----------- Resource Creation Functions ----------- 
def request_post(url, headers, body):
    try:
        res = requests.post(url, headers=headers, json=body)
        return res.status_code == 201
    except Exception as e:
        print(f"[ERROR] Failed to send POST request: {e}")
        return False

def check_and_create_ae(base_url, cse, ae):
    target = f"{base_url}/{cse}/{ae}"
    try:
        if requests.get(target, headers=getHeaders).status_code == 200:
            return True
    except:
        pass

    headers = Headers(content_type='ae').headers
    body = {
        "m2m:ae": {
            "rn": ae,
            "api": "N.humid",
            "rr": True
        }
    }
    return request_post(f"{base_url}/{cse}", headers, body)

def check_and_create_cnt(base_url, cse, ae, cnt):
    target = f"{base_url}/{cse}/{ae}/{cnt}"
    try:
        if requests.get(target, headers=getHeaders).status_code == 200:
            return True
    except:
        pass

    headers = Headers(content_type='cnt').headers
    body = {
        "m2m:cnt": {
            "rn": cnt
        }
    }
    return request_post(f"{base_url}/{cse}/{ae}", headers, body)

def send_cin(base_url, cse, ae, cnt, value):
    headers = Headers(content_type='cin').headers
    body = {
        "m2m:cin": {
            "con": value
        }
    }
    return request_post(f"{base_url}/{cse}/{ae}/{cnt}", headers, body)

def check_server_reachable(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=3):
            return True
    except:
        return False

# ----------- Main ----------- 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-data', required=True)
    parser.add_argument('--Frequency', type=int, required=True)
    parser.add_argument('--Target-Server', required=True)
    parser.add_argument('--Port', required=True)
    parser.add_argument('--Registration', type=int, default=0)
    args = parser.parse_args()

    CSE = "TinyIoT"
    AE = "humidSensor"
    CNT = "humidity"

    BASE_URL = f"http://{args.Target_Server}:{args.Port}"

    # Validate server and port
    print("[CHECK] Validating server and port...")
    if not check_server_reachable(args.Target_Server, args.Port):
        print(f"[ERROR] Cannot connect to server: {args.Target_Server}:{args.Port}")
        sys.exit(1)

    # Resource registration
    if args.Registration == 1:
        print("[HUMID] Creating AE...")
        check_and_create_ae(BASE_URL, CSE, AE)
        print("[HUMID] Creating CNT...")
        check_and_create_cnt(BASE_URL, CSE, AE, CNT)

    # Load CSV
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
    error_threshold = 5
    wait_seconds = 5

    while True:
        if index >= len(data):
            print("[INFO] All data has been sent. Exiting.")
            break

        value = data[index]
        success = send_cin(BASE_URL, CSE, AE, CNT, value)

        if success:
            print(f"[HUMID] Successfully sent: {value}")
            index += 1
            error_count = 0
        else:
            error_count += 1
            print(f"[ERROR] Failed to send: {value} (Retrying in {wait_seconds} seconds)")
            time.sleep(wait_seconds)

            if error_count >= error_threshold:
                print("[ERROR] Repeated failures detected. Server might be down. Exiting.")
                break

        time.sleep(args.Frequency)
