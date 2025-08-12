import json
import uuid
import threading
import paho.mqtt.client as mqtt

class MqttOneM2MClient:
    def __init__(self, broker, port, origin, cse):
        self.broker = broker
        self.port = int(port)
        self.origin = origin
        self.cse = cse
        self.response_received = threading.Event()
        self.last_response = None

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.req_topic = f"/oneM2M/req/{self.origin}/{self.cse}/json"
        self.resp_topic = f"/oneM2M/resp/{self.origin}/{self.cse}/json"
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            self.client.subscribe(self.resp_topic)
            print(f"[MQTT] Connected to broker {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("[MQTT] Disconnected.")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connection successful.")
        else:
            print(f"[MQTT] Connection failed with code {rc}.")

    def on_message(self, client, userdata, msg):
        try:
            print(f"[MQTT] [RECV] Topic: {msg.topic}")
            print(f"[MQTT] [RECV] Payload: {msg.payload.decode()}")
            payload = json.loads(msg.payload.decode())
            self.last_response = payload
            self.response_received.set()
        except Exception as e:
            print(f"[ERROR] Failed to parse MQTT response: {e}")

    def _send_request(self, body):
        request_id = str(uuid.uuid4())
        message = {
            "m2m:rqp": {
                "fr": self.origin,
                "to": body["to"],
                "op": body["op"],
                "rqi": request_id,
                "ty": body.get("ty"),
                "pc": body.get("pc", {})
            }
        }

        print(f"[MQTT] [SEND] Topic: {self.req_topic}")
        print(f"[MQTT] [SEND] Payload:")
        print(json.dumps(message, indent=2))

        self.response_received.clear()
        self.client.publish(self.req_topic, json.dumps(message))

        if self.response_received.wait(timeout=5):
            return True
        else:
            print("[ERROR] No MQTT response received within timeout.")
            return False

    def create_ae(self, ae_name):
        return self._send_request({
            "to": f"/{self.cse}",
            "op": 1,
            "ty": 2,
            "pc": {
                "m2m:ae": {
                    "rn": ae_name,
                    "api": "N.device",
                    "rr": True
                }
            }
        })

    def create_cnt(self, ae_name, cnt_name):
        return self._send_request({
            "to": f"/{self.cse}/{ae_name}",
            "op": 1,
            "ty": 3,
            "pc": {
                "m2m:cnt": {
                    "rn": cnt_name
                }
            }
        })

    def send_cin(self, ae_name, cnt_name, value):
        return self._send_request({
            "to": f"/{self.cse}/{ae_name}/{cnt_name}",
            "op": 1,
            "ty": 4,
            "pc": {
                "m2m:cin": {
                    "con": value
                }
            }
        })
