# Coordinator Script for tinyIoT and device simulator

## Overview
This project provides:
- **Device simulators** for sending arbitrary temperature and humidity data to a tinyIoT server  
- A **coordinator script** to control and manage all processes  

The simulators follow the **oneM2M standard** and support both **HTTP** and **MQTT** protocols for data transmission.  

## File Structure
- `coordinator.py` – Main script to control the tinyIoT server and simulators  
- `simulator.py` – Temperature & Humidity sensor simulator (It is possible to add sensors to suit the user’s situation.)
- `config_coord.py`- Global configuration values (coordiantion.py)    
- `config_sim.py` – Global configuration values (simulator.py)  
- `test_data_temp.csv` – Temperature CSV data  
- `test_data_humid.csv` – Humidity CSV data  

## Features
- **Integrated control** with `coordination.py`  
- **Temperature and humidity simulation**
- **Protocols**: Choose between **HTTP** or **MQTT**    
- **Modes**  
  - `csv`: Sends data from CSV files in sequence  
  - `random`: Generates random data within configured ranges  
- **Automatic registration**: Create oneM2M AE/CNT resources with `--Registration` option  

## Environment
- **OS**: Ubuntu 24.04.2 LTS  
- **Language**: Python 3.8+  
- **IoT**: [tinyIoT](https://github.com/seslabSJU/tinyIoT)
  <img width="90" height="45" alt="image" src="https://github.com/user-attachments/assets/4ae1149b-fd7f-43a2-bb53-f2e742399279" />
- **MQTT Broker**: [Mosquitto](https://mosquitto.org)  

## Installation


### 1. tinyIoT Setup 
#### (If you’ve already completed the tinyIoT environment setup from the simulator.py GitHub repository, you can omit this.)

- Access the tinyIoT GitHub repository
```bash
[Clone and build tinyIoT](https://github.com/seslabSJU/tinyIoT) according to its README.
```


- tinyIoT config.h settings
1. Verify that the following settings are correctly configured (Configure the IP and port as appropriate for your setup):


<img width="684" height="241" alt="image" src="https://github.com/user-attachments/assets/705a3ac5-4dec-4bbc-b35a-976ae12d600b" />


2. Uncomment #define ENABLE_MQTT.


<img width="641" height="397" alt="image" src="https://github.com/user-attachments/assets/6b856bbc-0dc7-46b9-bcd9-9a606407592f" />


### 2. simulator Setup
```bash
https://github.com/parksiwoo-1/Device_simulator_for_tinyIoT
```
Go to the relevant URL and set up the environment according to the README on the simulator’s GitHub.


## Run the Device Simulator Using the Coordinator Script
### Clone Repository
1. Navigate to the directory where you want to clone in Ubuntu:

```bash
cd tinyIoT/script   #example path
```


2. Clone

```bash
git clone https://github.com/parksiwoo-1/Coordination_script_and_Device_simulators_for_tinyIoT
```


3. Setting
  3.1 In config_coord.py, for images other than Ubuntu, set the path to simulator.py to match the user’s environment.
   <img width="759" height="212" alt="image" src="https://github.com/user-attachments/assets/e635e4ca-203e-4902-a43b-ac1fd094a273" />

   3.2 Modify the contents of config_coord.py shown in the image below to suit your needs
  <img width="681" height="100" alt="image" src="https://github.com/user-attachments/assets/817704a5-d6ce-45de-9e15-e155f9d4f32b" />
  <img width="907" height="121" alt="image" src="https://github.com/user-attachments/assets/bf000381-91d1-47bb-af20-2f15d8dbe9e2" />

4. option setting in coordinator.py

5. Set the options in `coordinator.py`.  
More detailed option settings can be configured in `config_coord.py`.
For more detailed descriptions of the options, refer to the man page.
- protocol : HTTP or MQTT

- mode : csv or random

- frequency : Data transmission interval (seconds)

- registration : 0 or 1 (Enable AE/CNT auto-registration)


5. Enter the cloned directory

```bash
cd tinyIoT/script   # example path
```


6. Run Coordinator Script

```bash
python3 coordinator.py
```
