import os
import re
import time
import logging
import subprocess
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
SWITCH_IP = os.getenv("SWITCH_IP", "192.168.1.1")
LOCATION = os.getenv("LOCATION", "01")
PING_INTERVAL = int(os.getenv("PING_INTERVAL", "5"))
TOPIC = f"harryspace/{LOCATION}/ping"

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)


def connect_mqtt():
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            logging.info("[MQTT] Connected")
            return
        except Exception as exc:
            logging.error("[MQTT] Connection failed; retrying in 5 seconds: %s", exc)
            time.sleep(5)


def ping_once(host):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None
        match = re.search(r"time[=<]([\d.]+)", result.stdout)
        return float(match.group(1)) if match else None
    except Exception as exc:
        logging.exception("[PING] Error pinging %s: %s", host, exc)
        return None


def main():
    connect_mqtt()
    logging.info("[PING] Starting ping monitor. Target=%s | Topic=%s", SWITCH_IP, TOPIC)
    while True:
        latency = ping_once(SWITCH_IP)
        if latency is not None:
            client.publish(TOPIC, str(latency))
            logging.info("[PING] %s = %.2f ms", SWITCH_IP, latency)
        else:
            client.publish(TOPIC, "-1")
            logging.warning("[PING] %s unreachable", SWITCH_IP)
        time.sleep(PING_INTERVAL)


if __name__ == "__main__":
    main()
