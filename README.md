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

  <img width="584" height="208" alt="image" src="https://github.com/user-attachments/assets/4ae1149b-fd7f-43a2-bb53-f2e742399279" />

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
- Access the tinyIoT GitHub repository
```bash
[Clone and build tinyIoT](https://github.com/seslabSJU/tinyIoT) according to its README.
```




- tinyIoT config.h settings
1. Verify that the following settings are correctly configured:


<img width="684" height="241" alt="image" src="https://github.com/user-attachments/assets/705a3ac5-4dec-4bbc-b35a-976ae12d600b" />


2. Uncomment #define ENABLE_MQTT.


<img width="641" height="397" alt="image" src="https://github.com/user-attachments/assets/6b856bbc-0dc7-46b9-bcd9-9a606407592f" />


### MQTT Broker (Mosquitto) Setup
- **Mosquitto installation required**

1. Visit the website  
   [https://mosquitto.org](https://mosquitto.org)  

2. Click **Download** in website

3. For Windows, download the x64 installer:


```bash   
mosquitto-2.0.22-install-windows-x64.exe
```


4. Edit mosquitto.conf:

- add #listener 1883, #protocol mqtt


<img width="2043" height="282" alt="image" src="https://github.com/user-attachments/assets/6c97477f-eb28-4d64-b71a-f249ff1336cb" />


5 Run  
Execute in Windows PowerShell using WSL:  


```bash
sudo systemctl start mosquitto
```


```bash
sudo systemctl status mosquitto
```


<img width="2162" height="632" alt="image" src="https://github.com/user-attachments/assets/bad124a0-6891-43fe-8ed4-8a9bef79c4ea" />


If it shows "active (running)" as in the image above, the broker setup is complete.


## Run Coordination Script & Device Simulators
### Clone Repository
1. Navigate to the directory where you want to clone in Ubuntu:

```bash
cd tinyIoT/script   #example path
```


2. Clone

```bash
git clone https://github.com/parksiwoo-1/Coordination_script_and_Device_simulators_for_tinyIoT
```

3. Enter the cloned directory

```bash
cd tinyIoT/script   # example path
```

4. Set the options in `coordination.py`.  
More detailed option settings can be configured in `config.py`.
For more detailed descriptions of the options, refer to the man page.
- protocol : HTTP or MQTT

- mode : csv or random

- frequency : Data transmission interval (seconds)

- registration : 0 or 1 (Enable AE/CNT auto-registration)




5. Run Coordination Script & Simulator

```bash
python3 coordination.py
```


## Man page
### coordination

COORDINATION.PY(1)                            IoT Device Coordination Manual                           COORDINATION.PY(1)

NAME
       coordination.py - coordination script for controlling and executing tinyIoT server and device simulators

SYNOPSIS
       python3 coordination.py

DESCRIPTION
       The coordination.py script runs the tinyIoT server and sequentially executes the temperature simulator
       (simulator_temp.py) and humidity simulator (simulator_humid.py) to control the overall IoT simulation environment.
       It checks the server response, detects whether each simulator is running normally, and safely terminates
       all processes if a failure occurs.

FUNCTIONALITY
       - Start the tinyIoT server and wait for its response.
       - Verify server responsiveness; terminate if the check fails.
       - Execute the temperature and humidity simulators with the specified parameters (protocol, mode, frequency, registration).
       - Verify that each simulator is running correctly.
       - Perform graceful shutdown upon receiving a KeyboardInterrupt during execution.

OPTIONS
       coordination.py itself does not have command-line options. Parameters for the simulators it runs are hardcoded.
       The following options are passed to each simulator:

       --protocol
              Specifies the data transmission protocol (http or mqtt).

       --mode
              Specifies the type of data to transmit (csv or random).

       --frequency
              Sets the data transmission interval in seconds.

       --registration
              Determines whether to create AE and CNT resources (1 = create, 0 = do not create).

FILES
       tinyIoT
              The lightweight oneM2M-based IoT server executed by coordination.py.

       simulator_temp.py
              Simulator script acting as a temperature sensor.

       simulator_humid.py
              Simulator script acting as a humidity sensor.
      
       mqtt_client.py
              Module responsible for MQTT-based oneM2M message transmission in simulators.

       config.py
              Configuration file containing server execution path, wait times, timeouts, and other settings used by coordination.py.

EXIT STATUS
       0      All processes executed successfully.

       1      Terminated due to server response failure, simulator execution failure, or an exception.

SEE ALSO
       simulator_temp.py(1), simulator_humid.py(1), config.py(5)

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       This script does not follow a specific license and may be freely used in local environments for learning or testing purposes.

September 6, 2025                                                                                      COORDINATION.PY(1)



### simulator_temp

SIMULATOR_TEMP.PY(1)                         IoT Sensor Simulator Manual                          SIMULATOR_TEMP.PY(1)

NAME
       simulator_temp.py - device simulator that emulates a temperature sensor and transmits data to tinyIoT using oneM2M

SYNOPSIS
       python3 simulator_temp.py --protocol {http|mqtt} --mode {csv|random} --frequency N (seconds) --registration [0|1]

DESCRIPTION
       simulator_temp.py is a device simulator that emulates a temperature sensor, generating sensor data at a specified
       interval and transmitting it as a oneM2M-compliant ContentInstance message. Both HTTP and MQTT protocols are
       supported, and the transmitted data can be selected either from a CSV file or generated randomly.

       Additionally, AE (Application Entity) and CNT (Container) resources can be pre-registered on the server if required.

OPTIONS
       --protocol {http|mqtt}
              Selects the data transmission protocol. http uses the REST API method, while mqtt transmits via an MQTT broker.

       --mode {csv|random}
              Determines how the data to be transmitted is selected. csv reads from a predefined CSV file and transmits
              sequentially, while random generates data according to the configured profile.

       --frequency N
              Specifies the interval, in seconds, at which sensor data is transmitted.

       --registration 0|1
              Sets whether AE and CNT resources should be registered on the server. 1 performs registration, 0 transmits without registration.

FUNCTIONALITY
       - Checks HTTP connectivity in advance.
       - When using MQTT protocol, connects to and disconnects from the broker.
       - If the registration option is set to 1, checks for AE and CNT on the server and creates them if they do not exist.
       - In CSV mode, reads and transmits data sequentially from the file; in random mode, generates data based on profile settings.
       - For HTTP transmission, verifies POST success and uses `/la` request as an additional confirmation if needed.
       - Retries upon errors, and terminates if repeated failures exceed the threshold.

FILES
       config.py
              Configuration file defining key parameters such as server settings, transmission interval, file paths, and error thresholds.

       mqtt_client.py
              Module implementing a oneM2M-based client for MQTT transmission.

       TEMP_CSV (config.TEMP_CSV)
              Path to the sensor data file used in CSV mode.

ENVIRONMENT VARIABLES
       All configurations are defined in config.py; environment variables are not used.

EXIT STATUS
       0      Normal termination.

       1      Termination due to configuration file errors, server connection failure, data file loading failure,
              AE/CNT registration failure, or repeated transmission errors.

SEE ALSO
       mqtt_client.py(1), config.py(5), simulator_humid.py(1)

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       This script does not follow an open license and may be freely used in local environments for testing and research purposes.

September 6, 2025                                                                                  SIMULATOR_TEMP.PY(1)


### simulator_humid

SIMULATOR_HUMID.PY(1)                         IoT Sensor Simulator Manual                          SIMULATOR_HUMID.PY(1)

NAME
       simulator_humid.py - device simulator that emulates a humidity sensor and transmits data to tinyIoT using oneM2M

SYNOPSIS
       python3 simulator_humid.py --protocol {http|mqtt} --mode {csv|random} --frequency N (seconds) --registration [0|1]

DESCRIPTION
       simulator_humid.py is a device simulator that emulates a humidity sensor, generating sensor data at a specified
       interval and transmitting it as a oneM2M-compliant ContentInstance message. Both HTTP and MQTT protocols are
       supported, and the transmitted data can be selected either from a CSV file or generated randomly.

       Additionally, AE (Application Entity) and CNT (Container) resources can be pre-registered on the server if required.

OPTIONS
       --protocol {http|mqtt}
              Selects the data transmission protocol. http uses the REST API method, while mqtt transmits via an MQTT broker.

       --mode {csv|random}
              Determines how the data to be transmitted is selected. csv reads from a predefined CSV file and transmits
              sequentially, while random generates data according to the configured profile.

       --frequency N
              Specifies the interval, in seconds, at which sensor data is transmitted.

       --registration 0|1
              Sets whether AE and CNT resources should be registered on the server. 1 performs registration, 0 transmits without registration.

FUNCTIONALITY
       - Checks HTTP connectivity in advance.
       - When using MQTT protocol, connects to and disconnects from the broker.
       - If the registration option is set to 1, checks for AE and CNT on the server and creates them if they do not exist.
       - In CSV mode, reads and transmits data sequentially from the file; in random mode, generates data based on profile settings.
       - For HTTP transmission, verifies POST success and uses `/la` request as an additional confirmation if needed.
       - Retries upon errors, and terminates if repeated failures exceed the threshold.

FILES
       config.py
              Configuration file defining key parameters such as server settings, transmission interval, file paths, and error thresholds.

       mqtt_client.py
              Module implementing a oneM2M-based client for MQTT transmission.

       HUMID_CSV (config.HUMID_CSV)
              Path to the sensor data file used in CSV mode.

ENVIRONMENT VARIABLES
       All configurations are defined in config.py; environment variables are not used.

EXIT STATUS
       0      Normal termination.

       1      Termination due to configuration file errors, server connection failure, data file loading failure,
              AE/CNT registration failure, or repeated transmission errors.

SEE ALSO
       mqtt_client.py(1), config.py(5), simulator_temp.py(1)

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       This script does not follow an open license and may be freely used in local environments for testing and research purposes.

September 6, 2025                                                                                  SIMULATOR_HUMID.PY(1)


### mqtt_client

MQTT_CLIENT.PY(1)                          IoT MQTT Module Manual                              MQTT_CLIENT.PY(1)

NAME
       mqtt_client.py - client module for performing MQTT communication based on oneM2M structure

SYNOPSIS
       from mqtt_client import MqttOneM2MClient

DESCRIPTION
       mqtt_client.py is a dedicated client module that handles sending and receiving messages through an MQTT broker
       (mosquitto) in accordance with the oneM2M standard message format, including the creation of AE, CNT, and CIN.
       It is mainly used in sensor simulators and can communicate with the tinyIoT platform or other oneM2M-compatible
       CSEs.

CLASS
       MqttOneM2MClient(broker, port, origin, cse_csi, cse_rn="TinyIoT")
              Initializes the object with MQTT broker address, port, origin identifier, and CSE-ID.
              Default request and response topics are set according to the oneM2M format.

METHODS
       connect()
              Connects to the MQTT broker and subscribes to the response topic.
              Returns True if the connection succeeds, otherwise False.

       disconnect()
              Terminates the MQTT connection and stops the loop.

       create_ae(ae_name)
              Sends a request to create an AE (Application Entity).
              If the AE already exists, it proceeds without error.
              Returns True or False depending on the result.

       create_cnt(ae_name, cnt_name)
              Creates a CNT (Container) under the specified AE.
              If it already exists, the request is ignored.

       send_cin(ae_name, cnt_name, value)
              Sends a ContentInstance (CIN) to the specified container.
              The value is a string and is wrapped in oneM2M format before transmission.

INTERNAL LOGIC
       - All transmission requests are handled inside the _send_request() function, where a UUID-based request ID (rqi) is automatically generated.
       - Response reception is handled using the response_received event and the on_message callback.
       - If no response is received within a specified timeout (default 5 seconds), it is treated as a timeout.
       - Response codes (rsc) are evaluated based on oneM2M standard codes (e.g., 2001: created, 4105: already exists).

TOPICS
       Request Topic:
              /oneM2M/req/{origin}/{cse_id}/json

       Response Topic:
              /oneM2M/resp/{origin}/{cse_id}/json

DEPENDENCIES
       - paho-mqtt
       - json
       - threading
       - uuid

USAGE EXAMPLE
       mqtt = MqttOneM2MClient("localhost", 1883, "Sensor01", "TinyIoT")
       mqtt.connect()
       mqtt.create_ae("Sensor01")
       mqtt.create_cnt("Sensor01", "temperature")
       mqtt.send_cin("Sensor01", "temperature", "23.5")
       mqtt.disconnect()

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       This module is freely available for research and development purposes for MQTT-based IoT communication.

September 2025                                                                           MQTT_CLIENT.PY(1)


### config

CONFIG.PY(5)                       IoT Script & Simulator Configuration                       CONFIG.PY(5)

NAME
       config.py - common configuration file for running IoT scripts and simulators

SYNOPSIS
       import config

DESCRIPTION
       config.py contains the shared configuration values used across the entire system, including coordination.py,
       simulator_temp.py, simulator_humid.py, and related components. It defines HTTP and MQTT server information,
       path settings, timing parameters, and sensor data profiles.

SETTINGS

       # tinyIoT
       SERVER_EXEC
              Specifies the execution path of the tinyIoT C server as a string.

       CSE_NAME
              Defines the csi (CSE-ID) of the CSE. Used in MQTT topic paths.

       CSE_RN
              Defines the resource name (rn) of the CSE. Used as the target path in HTTP and MQTT payloads.

       # HTTP settings
       HTTP_HOST
              The HTTP server address. Default is 127.0.0.1.
       
       HTTP_PORT
              The HTTP server port number. Default is 3000.
       
       HTTP_BASE
              Base HTTP URL, constructed from HTTP_HOST and HTTP_PORT.
       
       CSE_URL
              The CSE URL used for HTTP-based oneM2M requests. Example: http://127.0.0.1:3000/tinyiot

       # MQTT (Mosquitto) settings
       MQTT_HOST
              MQTT broker address.
       
       MQTT_PORT
              MQTT broker port number.

       # Time & Retry
       WAIT_SERVER_TIMEOUT
              Maximum wait time (in seconds) for server response, used in coordination.py.
       
       WAIT_PROCESS_TIMEOUT
              Time to wait when checking if simulator processes are running.
       
       RETRY_WAIT_SECONDS
              Wait time before retrying after a transmission failure.
       
       SEND_ERROR_THRESHOLD
              Allowed number of consecutive failures. Exceeding this will cause the script to terminate.
       
       PROCESS_START_DELAY
              Delay before starting simulators after launching the server.
       
       REQUEST_TIMEOUT
              Default timeout for HTTP requests.

       # CSV Paths
       TEMP_CSV
              Path to the CSV file for temperature sensor test data.
       
       HUMID_CSV
              Path to the CSV file for humidity sensor test data.

       # Device Profiles (Random Mode)
       TEMP_PROFILE
              Profile used when the temperature sensor operates in random mode. Supports int/float with min/max values.
     
       HUMID_PROFILE
              Profile used when the humidity sensor operates in random mode. Supports int/float with min/max values.

FILES
       This file is not executed directly, but imported by other scripts such as simulators and coordination modules.

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       Freely usable in research and experimental simulation environments.

April 06, 2025                                                                           CONFIG.PY(5)

