"""Publish synthetic DC-load telemetry to MQTT."""

import json
import logging
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("hems.simulator")

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "hems/v1").strip("/")
DEVICE_ID = os.getenv("SIMULATOR_DEVICE_ID", "sim-load-01")
INTERVAL = max(0.2, float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "2")))


def build_payload() -> dict:
    """Generate synthetic values for a low-voltage DC load."""
    voltage_v = round(random.uniform(11.8, 12.4), 3)
    current_a = round(random.uniform(0.10, 1.20), 3)
    power_w = round(voltage_v * current_a, 3)

    return {
        "schema_version": 1,
        "device_id": DEVICE_ID,
        "source": "simulation",
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "voltage_v": voltage_v,
        "current_a": current_a,
        "power_w": power_w,
    }


def main() -> None:
    topic = f"{TOPIC_PREFIX}/telemetry/{DEVICE_ID}"
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"hems-simulator-{DEVICE_ID}",
        protocol=mqtt.MQTTv311,
    )

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info("Connected to MQTT broker at %s:%s", MQTT_HOST, MQTT_PORT)
            logger.info("Publishing to %s every %.1f seconds", topic, INTERVAL)
        else:
            logger.error("MQTT connection failed: %s", reason_code)

    client.on_connect = on_connect

    try:
        client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()
        while True:
            payload = build_payload()
            info = client.publish(
                topic,
                payload=json.dumps(payload, ensure_ascii=False),
                qos=0,
                retain=False,
            )
            info.wait_for_publish()
            logger.info(
                "PUBLISHED | V=%.3f V | I=%.3f A | P=%.3f W",
                payload["voltage_v"],
                payload["current_a"],
                payload["power_w"],
            )
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logger.info("Simulator stopped.")
    except OSError as exc:
        logger.error("Cannot connect to MQTT broker: %s", exc)
        raise SystemExit(1) from exc
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
