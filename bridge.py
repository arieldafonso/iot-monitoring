import logging
import os
import time

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = "harryspace/+/+"

INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
INFLUX_DB = os.getenv("INFLUX_DB", "harryspace")
INFLUX_USER = os.getenv("INFLUX_USER", "user")
INFLUX_PASSWORD = os.getenv("INFLUX_PASSWORD", "password")

VALID_MEASUREMENTS = {"temperature", "humidity", "lux", "voltage", "presence", "ping"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def ensure_influx_database(client):
    try:
        databases = [database["name"] for database in client.get_list_database()]
    except Exception as exc:
        logging.exception("Unable to list InfluxDB databases: %s", exc)
        raise

    if INFLUX_DB not in databases:
        client.create_database(INFLUX_DB)
        logging.info("[INFLUXDB] Database %s created.", INFLUX_DB)
    else:
        logging.info("[INFLUXDB] Database %s ready.", INFLUX_DB)


influx_client = InfluxDBClient(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASSWORD,
    database=INFLUX_DB,
)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("[MQTT] Connected")
        client.subscribe(MQTT_TOPIC)
        logging.info("[MQTT] Subscribed: %s", MQTT_TOPIC)
    else:
        logging.error("[MQTT] Connection failed with rc=%s", rc)


def on_disconnect(client, userdata, rc):
    logging.warning("[MQTT] Disconnected (rc=%s). Reconnecting...", rc)


def on_message(client, userdata, msg):
    topic = msg.topic.strip()
    payload = msg.payload.decode("utf-8", "replace").strip()

    if not topic:
        logging.warning("[MQTT] Ignoring empty topic.")
        return

    logging.info("[MQTT] Received: %s = %s", topic, payload)

    parts = topic.split("/")
    if len(parts) != 3 or parts[0] != "harryspace":
        logging.warning("[MQTT] Ignoring invalid topic: %s", topic)
        return

    location, measurement = parts[1], parts[2]
    if measurement not in VALID_MEASUREMENTS:
        logging.warning("[MQTT] Ignoring unknown measurement '%s' from topic %s", measurement, topic)
        return

    if not payload:
        logging.warning("[MQTT] Ignoring empty payload for %s", topic)
        return

    try:
        numeric_value = float(payload)
    except ValueError:
        logging.warning("[MQTT] Ignoring non-numeric payload for %s: %s", topic, payload)
        return

    data = [{
        "measurement": measurement,
        "tags": {"location": location},
        "fields": {"value": numeric_value},
    }]

    try:
        influx_client.write_points(data, database=INFLUX_DB, time_precision="s")
        logging.info("[INFLUXDB] Saved: %s = %s location=%s", measurement, numeric_value, location)
    except Exception as exc:
        logging.exception("[INFLUXDB] Failed to save data for %s: %s", topic, exc)


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect


def connect_mqtt_with_retry():
    while True:
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.loop_start()
            return
        except Exception as exc:
            logging.exception("[MQTT] Connection failed; retrying in 5 seconds: %s", exc)
            time.sleep(5)


def connect_influx_with_retry():
    while True:
        try:
            influx_client.ping()
            ensure_influx_database(influx_client)
            return
        except Exception as exc:
            logging.exception("[INFLUXDB] Connection failed; retrying in 5 seconds: %s", exc)
            time.sleep(5)


def main():
    logging.info("[BRIDGE] Starting bridge. MQTT=%s:%s | InfluxDB=%s:%s | DB=%s",
                 MQTT_BROKER, MQTT_PORT, INFLUX_HOST, INFLUX_PORT, INFLUX_DB)

    connect_influx_with_retry()
    connect_mqtt_with_retry()

    try:
        while True:
            if not mqtt_client.is_connected():
                logging.warning("[MQTT] Client disconnected; attempting reconnect.")
                connect_mqtt_with_retry()
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("[BRIDGE] Shutting down gracefully.")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        influx_client.close()


if __name__ == "__main__":
    main()
