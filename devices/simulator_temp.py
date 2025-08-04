import argparse
import csv
import time
import requests
import socket
import sys
import urllib3

urllib3.disable_warnings()

# ----------- oneM2M 기본 설정 -----------
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

getHeaders = {
    'Accept': 'application/json',
    'X-M2M-Origin': 'CAdmin',
    'X-M2M-RVI': '3',
    'X-M2M-RI': 'check'
}

# ----------- 리소스 생성 함수 -----------
def request_post(url, headers, body, verify_ssl):
    try:
        res = requests.post(url, headers=headers, json=body, verify=verify_ssl)
        return res.status_code == 201
    except Exception as e:
        print(f"[ERROR] POST 요청 실패: {e}")
        return False

def check_and_create_ae(base_url, cse, ae, verify_ssl):
    target = f"{base_url}/{cse}/{ae}"
    try:
        if requests.get(target, headers=getHeaders, verify=verify_ssl).status_code == 200:
            return True
    except:
        pass

    headers = Headers(content_type='ae').headers
    body = {
        "m2m:ae": {
            "rn": ae,
            "api": "N.temp",
            "rr": True
        }
    }
    return request_post(f"{base_url}/{cse}", headers, body, verify_ssl)

def check_and_create_cnt(base_url, cse, ae, cnt, verify_ssl):
    target = f"{base_url}/{cse}/{ae}/{cnt}"
    try:
        if requests.get(target, headers=getHeaders, verify=verify_ssl).status_code == 200:
            return True
    except:
        pass

    headers = Headers(content_type='cnt').headers
    body = {
        "m2m:cnt": {
            "rn": cnt
        }
    }
    return request_post(f"{base_url}/{cse}/{ae}", headers, body, verify_ssl)

def send_cin(base_url, cse, ae, cnt, value, verify_ssl):
    headers = Headers(content_type='cin').headers
    body = {
        "m2m:cin": {
            "con": value
        }
    }
    return request_post(f"{base_url}/{cse}/{ae}/{cnt}", headers, body, verify_ssl)

def check_server_reachable(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=3):
            return True
    except:
        return False

# ----------- main -----------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-data', required=True)
    parser.add_argument('--Frequency', type=int, required=True)
    parser.add_argument('--Target-Server', required=True)
    parser.add_argument('--Port', required=True)
    parser.add_argument('--Registration', type=int, default=0)
    parser.add_argument('--Use-HTTPS', type=int, default=0, help='1이면 HTTPS 사용')
    parser.add_argument('--Verify-Cert', type=int, default=0, help='1이면 인증서 검증')
    args = parser.parse_args()

    protocol = "https" if args.Use_HTTPS else "http"
    BASE_URL = f"{protocol}://{args.Target-Server}:{args.Port}"
    verify_ssl = args.Verify_Cert == 1

    CSE = "TinyIoT"
    AE = "tempSensor"
    CNT = "temperature"

    print("[CHECK] 서버 및 포트 확인 중...")
    if not check_server_reachable(args.Target_Server, args.Port):
        print(f"[ERROR] 서버에 연결할 수 없습니다: {args.Target_Server}:{args.Port}")
        sys.exit(1)

    if args.Registration == 1:
        print("[TEMP] AE 생성 중...")
        check_and_create_ae(BASE_URL, CSE, AE, verify_ssl)
        print("[TEMP] CNT 생성 중...")
        check_and_create_cnt(BASE_URL, CSE, AE, CNT, verify_ssl)

    try:
        with open(args.input_data, 'r') as file:
            reader = list(csv.reader(file))
            data = [row[0].strip() for row in reader if row]
    except Exception as e:
        print(f"[ERROR] CSV 파일 열기 실패: {e}")
        sys.exit(1)

    if not data:
        print("[ERROR] CSV 데이터가 비어 있습니다.")
        sys.exit(1)

    print("[TEMP] 데이터 전송 시작...")
    index = 0
    error_count = 0
    error_threshold = 5
    wait_seconds = 5

    while True:
        if index >= len(data):
            print("[INFO] 모든 데이터를 전송했습니다. 종료합니다.")
            break

        value = data[index]
        success = send_cin(BASE_URL, CSE, AE, CNT, value, verify_ssl)

        if success:
            print(f"[TEMP] 전송 성공: {value}")
            index += 1
            error_count = 0
        else:
            error_count += 1
            print(f"[ERROR] 전송 실패: {value} (재시도 대기 중 {wait_seconds}초)")
            time.sleep(wait_seconds)

            if error_count >= error_threshold:
                print("[ERROR] 연속 실패 발생. 서버 상태 이상. 종료합니다.")
                break

        time.sleep(args.Frequency)
