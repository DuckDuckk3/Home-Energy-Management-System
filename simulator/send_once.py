"""Publish one deterministic test message to validate the MQTT path."""

import json
import logging
import os
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("hems.test-publisher")

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "hems/v1").strip("/")
DEVICE_ID = "test-device-01"


def main() -> None:
    topic = f"{TOPIC_PREFIX}/telemetry/{DEVICE_ID}"
    payload = {
        "schema_version": 1,
        "device_id": DEVICE_ID,
        "source": "manual_test",
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "voltage_v": 12.0,
        "current_a": 0.5,
        "power_w": 6.0,
    }

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="hems-one-shot-test",
        protocol=mqtt.MQTTv311,
    )
    try:
        client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()
        info = client.publish(topic, json.dumps(payload), qos=0, retain=False)
        info.wait_for_publish()
        logger.info("Published one test message to %s", topic)
    except OSError as exc:
        logger.error("Cannot connect to MQTT broker: %s", exc)
        raise SystemExit(1) from exc
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
