import json
import uuid
import threading
import paho.mqtt.client as mqtt
import config


class MqttOneM2MClient:
    def __init__(self, broker, port, origin, cse):
        self.broker = broker
        self.port = int(port)
        self.origin = origin
        self.cse = cse

        self.response_received = threading.Event()
        self.last_response = None

        print(f"[MQTT] Using module file: {__file__}")

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.req_topic = f"/oneM2M/req/{self.origin}/{self.cse}/json"
        self.resp_topic = f"/oneM2M/resp/{self.origin}/{self.cse}/json"

    def on_connect(self, client, userdata, flags, rc):
        print("[MQTT] Connection successful." if rc == 0 else f"[MQTT] Connection failed: rc={rc}")

    def on_disconnect(self, client, userdata, rc):
        print(f"[MQTT] Disconnected rc={rc}")

    def on_message(self, client, userdata, msg):
        try:
            print(f"[MQTT] [RECV] Topic: {msg.topic}")
            payload_txt = msg.payload.decode()
            print(f"[MQTT] [RECV] Payload: {payload_txt}")
            self.last_response = json.loads(payload_txt)
            self.response_received.set()
        except Exception as e:
            print(f"[ERROR] Failed to parse MQTT response: {e}")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            self.client.subscribe(self.resp_topic, qos=0)
            print(f"[MQTT] SUB {self.resp_topic}")
            print(f"[MQTT] Connected to broker {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        try:
            self.client.loop_stop()
        finally:
            self.client.disconnect()
        print("[MQTT] Disconnected.")

    def _send_request(self, body):
        request_id = str(uuid.uuid4())
        message = {
            "fr": self.origin,
            "to": body["to"],
            "op": body["op"],
            "rqi": request_id,
            "ty": body.get("ty"),
            "pc": body.get("pc", {}),
            "rvi": "3"
        }

        req_topic_with_origin = f"/oneM2M/req/{self.origin}/{self.cse}/json"

        print(f"[MQTT] [SEND] Topic: {req_topic_with_origin}")
        print(f"[MQTT] [SEND] Payload:")
        print(json.dumps(message, indent=2, ensure_ascii=False))

        self.response_received.clear()
        self.client.publish(req_topic_with_origin, json.dumps(message))

        if self.response_received.wait(timeout=5):
            return True
        print("[ERROR] No MQTT response received within timeout.")
        return False

    def create_ae(self, ae_name):
        return self._send_request({
            "to": f"/{self.cse}",
            "op": 1,
            "ty": 2,
            "pc": {"m2m:ae": {"rn": ae_name, "api": "N.device", "rr": True}}
        })

    def create_cnt(self, ae_name, cnt_name):
        return self._send_request({
            "to": f"/{self.cse}/{ae_name}",
            "op": 1,
            "ty": 3,
            "pc": {"m2m:cnt": {"rn": cnt_name}}
        })

    def send_cin(self, ae_name, cnt_name, value):
        return self._send_request({
            "to": f"/{self.cse}/{ae_name}/{cnt_name}",
            "op": 1,
            "ty": 4,
            "pc": {"m2m:cin": {"con": value}}
        })
