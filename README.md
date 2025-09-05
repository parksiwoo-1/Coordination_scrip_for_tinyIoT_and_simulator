# Coordination Script and Device Simulators for tinyIoT

## Overview
This project provides:
- **Device simulators** for sending arbitrary temperature and humidity data to a tinyIoT server  
- A **coordination script** to control and manage all processes  

The simulators follow the **oneM2M standard** and support both **HTTP** and **MQTT** protocols for data transmission.  

## File Structure
- `coordination.py` – Main script to control the tinyIoT server and simulators  
- `simulator_temp.py` – Temperature sensor simulator  
- `simulator_humid.py` – Humidity sensor simulator  
- `mqtt_client.py` – MQTT oneM2M communication module  
- `config.py` – Global configuration values  
- `test data/test_data_temp.csv` – Temperature CSV data  
- `test data/test_data_humid.csv` – Humidity CSV data  

## Features
- **Integrated control** with `coordination.py`  
- **Temperature and humidity simulation**  
- **Modes**  
  - `csv`: Sends data from CSV files in sequence  
  - `random`: Generates random data within configured ranges  
- **Protocols**: Choose between **HTTP** or **MQTT**  
- **Automatic registration**: Create oneM2M AE/CNT resources with `-Registration` option  

## Environment
- **OS**: Ubuntu 24.04.2 LTS  
- **Language**: Python 3.8+  
- **IoT**: [tinyIoT](https://github.com/seslabSJU/tinyIoT)  
- **MQTT Broker**: [Mosquitto](https://mosquitto.org)  

## Installation

### Python Libraries
```bash
pip install requests
```
```bash
pip install paho-mqtt
```

### tinyIoT Setup
-Access the tinyIoT GitHub repository
```bash
[Clone and build tinyIoT](https://github.com/seslabSJU/tinyIoT) according to its README.
```




-tinyIoT config.h settings
1. Verify that the following settings are correctly configured:


<img width="684" height="241" alt="image" src="https://github.com/user-attachments/assets/705a3ac5-4dec-4bbc-b35a-976ae12d600b" />


2. Uncomment #define ENABLE_MQTT.


<img width="641" height="397" alt="image" src="https://github.com/user-attachments/assets/6b856bbc-0dc7-46b9-bcd9-9a606407592f" />


### Mosquitto Setup
```bash
Install from mosquitto.org
```

Edit mosquitto.conf:

-add #listener 1883, #protocol mqtt


<img width="2043" height="282" alt="image" src="https://github.com/user-attachments/assets/6c97477f-eb28-4d64-b71a-f249ff1336cb" />


Start the broker:
```bash
sudo systemctl start mosquitto
```
```bash
sudo systemctl status mosquitto
```

## Run
### Clone Repository
```bash
git clone https://github.com/parksiwoo-1/Coordination_script_and_Device_simulators_for_tinyIoT
```
```bash
cd tinyIoT/script   # example path
```
- Coordination Script
```bash
python3 coordination.py
```

## Options

-Protocol : HTTP or MQTT

-Mode : csv or random

-FREQUENCY : Data transmission interval (seconds)

-Registration 1 : Enable AE/CNT auto-registration
