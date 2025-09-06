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
```bash
COORDINATION.PY(1)                       IoT Device Coordination Manual                        COORDINATION.PY(1)

NAME
       coordination.py - control and execution script coordinating tinyIoT server and device simulators

SYNOPSIS
       python3 coordination.py

DESCRIPTION
       coordination.py runs the tinyIoT server and sequentially launches the temperature simulator
       (simulator_temp.py) and humidity simulator (simulator_humid.py) to control the overall IoT simulation
       environment. It checks the server's responsiveness, detects whether each simulator is running properly, and
       safely terminates all processes in case of failure.

FUNCTIONALITY
       - Start the tinyIoT server and wait for its response.
       - Check if the server response is valid, terminate on failure.
       - Launch the temperature and humidity simulators with specified settings (protocol, mode, frequency, registration).
       - Confirm that each simulator is running properly.
       - Perform graceful shutdown on KeyboardInterrupt input during execution.

OPTIONS
       coordination.py does not take its own options; simulator parameters are hardcoded and passed internally:

       --protocol
              Specify the data transfer protocol (http or mqtt).

       --mode
              Select the type of data to send (csv or random).

       --frequency
              Set the data transfer interval in seconds.

       --registration
              Specify whether to create AE and CNT resources (1 = create, 0 = skip).

FILES
       tinyIoT
              OneM2M-based lightweight IoT server executed by coordination.py.

       simulator_temp.py
              Simulator script acting as a temperature sensor.

       simulator_humid.py
              Simulator script acting as a humidity sensor.

       mqtt_client.py
              Module handling MQTT-based oneM2M message transmission for simulators.

       config.py
              Configuration file containing server path, wait times, timeouts, and other parameters.

EXIT STATUS
       0      All processes executed successfully.

       1      Terminated due to server response failure, simulator startup failure, or exception.

SEE ALSO
       simulator_temp.py(1), simulator_humid.py(1), config.py(5)

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       This script does not follow a specific license and is freely usable in local environments for learning or
       testing purposes.

April 06, 2025                                                                              COORDINATION.PY(1)

SIMULATOR_TEMP.PY(1)                        IoT Sensor Simulator Manual                        SIMULATOR_TEMP.PY(1)

NAME
       simulator_temp.py - device simulator that emulates a temperature sensor and sends data to tinyIoT via oneM2M

SYNOPSIS
       python3 simulator_temp.py --protocol {http|mqtt} --mode {csv|random} --frequency N (seconds) --registration [0|1]

DESCRIPTION
       simulator_temp.py simulates a temperature sensor by generating sensor data at specified intervals and sending
       it as oneM2M-compliant ContentInstance messages. Both HTTP and MQTT protocols are supported, with data
       transmitted either from a CSV file or generated randomly.

       AE (Application Entity) and CNT (Container) resources can optionally be registered on the server.

OPTIONS
       --protocol {http|mqtt}
              Selects the transfer protocol. http uses REST API, mqtt sends data via MQTT broker.

       --mode {csv|random}
              Determines the data source. csv reads from a prepared CSV file, random generates values based on
              predefined profiles.

       --frequency N
              Specifies the interval in seconds between transmissions.

       --registration 0|1
              Controls whether AE and CNT resources are created on the server (1 = create, 0 = skip).

FUNCTIONALITY
       - Validates HTTP connectivity if protocol is http.
       - For MQTT, handles broker connection and disconnection.
       - Registers AE and CNT resources if registration is set to 1.
       - Sends sequential CSV data or random values depending on mode.
       - For HTTP, checks POST result and verifies storage via `/la` when necessary.
       - Retries on errors; terminates after repeated failures.

FILES
       config.py
              Defines parameters such as server settings, transmission frequency, file paths, and error thresholds.

       mqtt_client.py
              Implements oneM2M-compliant MQTT client for message transmission.

       TEMP_CSV (config.TEMP_CSV)
              Path to the CSV file used in csv mode.

ENVIRONMENT VARIABLES
       No environment variables are used; all settings are defined in config.py.

EXIT STATUS
       0      Successful completion.

       1      Exited due to configuration errors, server connection failure, data file errors, AE/CNT registration
              failure, or repeated transmission failures.

SEE ALSO
       mqtt_client.py(1), config.py(5), simulator_humid.py(1)

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       Freely usable in local environments for testing and research without any specific license.

April 06, 2025                                                                           SIMULATOR_TEMP.PY(1)

SIMULATOR_HUMID.PY(1)                       IoT Sensor Simulator Manual                        SIMULATOR_HUMID.PY(1)

NAME
       simulator_humid.py - device simulator that emulates a humidity sensor and sends data to tinyIoT via oneM2M

SYNOPSIS
       python3 simulator_humid.py --protocol {http|mqtt} --mode {csv|random} --frequency N (seconds) --registration [0|1]

DESCRIPTION
       simulator_humid.py simulates a humidity sensor by generating sensor data at specified intervals and sending
       it as oneM2M-compliant ContentInstance messages. Both HTTP and MQTT protocols are supported, with data
       transmitted either from a CSV file or generated randomly.

       AE (Application Entity) and CNT (Container) resources can optionally be registered on the server.

OPTIONS
       --protocol {http|mqtt}
              Selects the transfer protocol. http uses REST API, mqtt sends data via MQTT broker.

       --mode {csv|random}
              Determines the data source. csv reads from a prepared CSV file, random generates values based on
              predefined profiles.

       --frequency N
              Specifies the interval in seconds between transmissions.

       --registration 0|1
              Controls whether AE and CNT resources are created on the server (1 = create, 0 = skip).

FUNCTIONALITY
       - Validates HTTP connectivity if protocol is http.
       - For MQTT, handles broker connection and disconnection.
       - Registers AE and CNT resources if registration is set to 1.
       - Sends sequential CSV data or random values depending on mode.
       - For HTTP, checks POST result and verifies storage via `/la` when necessary.
       - Retries on errors; terminates after repeated failures.

FILES
       config.py
              Defines parameters such as server settings, transmission frequency, file paths, and error thresholds.

       mqtt_client.py
              Implements oneM2M-compliant MQTT client for message transmission.

       HUMID_CSV (config.HUMID_CSV)
              Path to the CSV file used in csv mode.

ENVIRONMENT VARIABLES
       No environment variables are used; all settings are defined in config.py.

EXIT STATUS
       0      Successful completion.

       1      Exited due to configuration errors, server connection failure, data file errors, AE/CNT registration
              failure, or repeated transmission failures.

SEE ALSO
       mqtt_client.py(1), config.py(5), simulator_temp.py(1)

AUTHOR
       Author: Siwoo Park <parksw@sju.ac.kr>

COPYRIGHT
       Freely usable in local environments for testing and research without any specific license.

April 06, 2025                                                                          SIMULATOR_HUMID.PY(1)

MQTT_CLIENT.PY(1)                           IoT MQTT Module Manual                           MQTT_CLIENT.PY(1)

NAME
       mqtt_client.py - client module for performing MQTT communication based on oneM2M structure

SYNOPSIS
       from mqtt_client import MqttOneM2MClient

DESCRIPTION
       mqtt_client.py is a dedicated client module that handles message transmission and reception via an MQTT
       broker (mosquitto) in oneM2M-compliant format. It supports operations such as AE, CNT, and CIN creation.
       It is mainly used by sensor simulators and can communicate with tinyIoT or other oneM2M-compatible CSEs.

CLASS
       MqttOneM2MClient(broker, port, origin, cse_csi, cse_rn="TinyIoT")
              Initializes an object with broker address, port, origin identifier, and CSE-ID. Request and response
              topics are set according to the oneM2M format.

METHODS
       connect()
              Connects to the MQTT broker and subscribes to the response topic. Returns True on success, False on
              failure.

       disconnect()
              Terminates the MQTT connection and stops the loop.

       create_ae(ae_name)
              Sends a request to create an AE (Application Entity). Continues without error if already existing.
              Returns True or False depending on result.

       create_cnt(ae_name, cnt_name)
              Creates a CNT (Container) under the given AE. Ignores duplicate creation.

       send_cin(ae_name, cnt_name, value)
              Sends a ContentInstance (CIN) to the specified container. Value is sent as a string in oneM2M format.

INTERNAL LOGIC
       - All requests are sent via the internal _send_request() function with UUID-based request IDs (rqi).
       - Responses are processed through the response_received event and the on_message callback.
       - Requests are considered timed out if no response is received within 5 seconds.
       - Response codes (rsc) are checked according to oneM2M standards (e.g., 2001: created, 4105: already exists).

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
       This module is freely usable for research and development of MQTT-based IoT communication.

April 06, 2025                                                                              MQTT_CLIENT.PY(1)

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

April 06, 2025                                                                                  CONFIG.PY(5)
```
