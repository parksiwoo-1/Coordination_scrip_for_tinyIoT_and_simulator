# Coordination script and Device simulators for tinyIoT



## coordination 스크립트 & 디바이스 시뮬레이터

이 프로젝트는 tinyIoT 서버에 임의의 온도와 습도 데이터를 전송하기 위해 개발된 디바이스 시뮬레이터와 이 모든 과정과 동작을 제어하는 coordination 스크립트로 구성되어 있습니다. coordination 스크립트를 통해 tinyIoT 서버와 디바이스 시뮬레이터들을 손쉽게 실행하고 관리할 수 있습니다. 디바이스 시뮬레이터들은 onem2m표준을 준수하며, HTTP 또는 MQTT 프로토콜을 사용하여 데이터(온도, 습도)를 전송합니다.



## 파일 구성

- `coordination.py`: tinyIoT 서버와 디바이스 시뮬레이터들을 제어하는 메인 스크립트
- `simulator_temp.py`: 온도 센서를 시뮬레이션하여 데이터를 전송
- `simulator_humid.py`: 습도 센서를 시뮬레이션하여 데이터를 전송
- `mqtt_client.py`: MQTT oneM2M 통신을 위한 모듈
- `config.py`: 프로젝트의 모든 전역 설정값
- `test data/test_data_temp.csv`: 온도 데이터 CSV 파일
- `test data/test_data_humid.csv`: 습도 데이터 CSV 파일



## 주요 기능

- **통합 제어**: coordination.py 스크립트 하나로 TinyIoT 서버와 여러 디바이스 시뮬레이터를 순차적으로 실행하고 종료합니다.
- **다양한 데이터 시뮬레이션**: 온도(simulator_temp.py)와 습도(simulator_humid.py) 데이터를 시뮬레이션합니다.
- **유연한 모드**:
    - **CSV 모드**: 미리 정의된 CSV 파일의 데이터를 순서대로 전송합니다.
    - **랜덤 모드**: config.py에 설정된 값 범위 내에서 임의의 데이터를 생성하여 전송합니다.
- **다중 프로토콜 지원**: HTTP 또는 MQTT 프로토콜을 선택하여 데이터를 전송할 수 있습니다.
- **자동 등록**: 시뮬레이터 시작 시, -Registration 옵션을 통해 oneM2M AE(Application Entity) 및 CNT(Container) 리소스를 자동으로 생성합니다.



## 사용 환경

- **언어**: Python 3
- **MQTT broker**: mosquitto
- **IoT**: tinyIoT



## 환경 설치

### 1. Python

- Python 3.8+
- 필요 라이브러리 설치:

```c
pip install paho-mqtt requests
```


### 2. MQTT 브로커

- Mosquitto 설치 필요:

1. 웹사이트 접속
```
https://mosquitto.org
```

2. Download 클릭

3. windows에 x64로 다운로드 진행
```
mosquitto-2.0.22-install-windows-x64.exe
```

- 설정:
설치한 경로에서 mosquitto.conf 파일을 찾아 수정을 해야 된다.

#listener 1883
#protocol mqtt
을 추가하면 된다.
<img width="902" height="129" alt="image" src="https://github.com/user-attachments/assets/8141a200-901c-44bd-9569-2ed83651e802" />



- 실행:

```c
sudo systemctl start mosquitto
```


### 3. tinyIoT

https://github.com/seslabSJU/tinyIoT

이것을 참조하여 tinyIoT에 대한 이해와 설치를 하면 된다.

tinyIoT config.h 설정
1.


<img width="684" height="241" alt="image" src="https://github.com/user-attachments/assets/705a3ac5-4dec-4bbc-b35a-976ae12d600b" />



2. #define ENABLE_MQTT의 주석을 제거해야 한다.



<img width="641" height="397" alt="image" src="https://github.com/user-attachments/assets/6b856bbc-0dc7-46b9-bcd9-9a606407592f" />



### 4. coordination 스크립트 &  디바이스 시뮬레이터

- 레파지토리 클론

```c
git clone https://github.com/parksiwoo-1/Coordination_script_and_Device_simulators_for_tinyIoT
```

원하는 경로로 진입하여 해당 명령어를 입력하면 한번에 클론할 수 있다.
(ex. tinyIoT/script)



## 실행 방법

### 1. 클론 한 경로로 진입

```c
cd tinyIoT/script
```
본인이 설정한 경로에 맞게 입력

### **2. coordination.py** (전체 제어)

```bash
python3 coordination.py
```

coordination.py에서 옵션을 설정하여 실행한다. 더 세부적인 옵션 설정은 config,py에서 할 수 있다.

- `-Protocol`: `HTTP` 또는 `MQTT`
- `-Mode`: `csv` 또는 `random`
- `-FREQUENCY` : 데이터 전송 주기를 결정 (seconds)
- `-Registration 1`: AE/CNT 자동 생성 설정
