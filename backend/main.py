"""MQTT telemetry receiver for the HEMS starter project."""

import json
import logging
import os
from datetime import datetime
from typing import Any

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("hems.backend")

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "hems/v1").strip("/")


def validate_telemetry(payload: Any) -> tuple[bool, str]:
    """Validate the minimum telemetry schema; this is not a physical sensor check."""
    if not isinstance(payload, dict):
        return False, "payload must be a JSON object"

    required = {
        "schema_version",
        "device_id",
        "source",
        "timestamp",
        "voltage_v",
        "current_a",
        "power_w",
    }
    missing = required - payload.keys()
    if missing:
        return False, f"missing fields: {', '.join(sorted(missing))}"

    if payload["schema_version"] != 1:
        return False, "unsupported schema_version"

    for field in ("device_id", "source", "timestamp"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            return False, f"{field} must be a non-empty string"

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False, "timestamp must be ISO 8601"

    for field in ("voltage_v", "current_a", "power_w"):
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f"{field} must be numeric"
        if value < 0:
            return False, f"{field} must be non-negative for this DC-load prototype"

    return True, "ok"


def on_connect(client: mqtt.Client, userdata: Any, flags: dict, reason_code: Any, properties: Any) -> None:
    if reason_code == 0:
        topic = f"{TOPIC_PREFIX}/telemetry/#"
        logger.info("Connected to MQTT broker at %s:%s", MQTT_HOST, MQTT_PORT)
        client.subscribe(topic, qos=0)
        logger.info("Subscribed to topic: %s", topic)
    else:
        logger.error("MQTT connection failed: %s", reason_code)


def on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
    raw = message.payload.decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("Rejected invalid JSON on %s: %s", message.topic, exc)
        return

    valid, reason = validate_telemetry(payload)
    if not valid:
        logger.warning("Rejected payload on %s: %s | raw=%s", message.topic, reason, raw)
        return

    # Check that topic device ID matches payload device ID.
    topic_parts = message.topic.split("/")
    topic_device_id = topic_parts[-1] if len(topic_parts) >= 4 else None
    if topic_device_id and topic_device_id != payload["device_id"]:
        logger.warning(
            "Topic/payload device mismatch: topic device=%s, payload device=%s",
            topic_device_id,
            payload["device_id"],
        )

    logger.info(
        "TELEMETRY | topic=%s | device=%s | source=%s | V=%.3f V | I=%.3f A | P=%.3f W | timestamp=%s",
        message.topic,
        payload["device_id"],
        payload["source"],
        payload["voltage_v"],
        payload["current_a"],
        payload["power_w"],
        payload["timestamp"],
    )


def main() -> None:
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="hems-backend-receiver",
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info("Starting HEMS telemetry backend...")
    logger.info("Broker: %s:%s | topic prefix: %s", MQTT_HOST, MQTT_PORT, TOPIC_PREFIX)

    try:
        client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    except OSError as exc:
        logger.error("Cannot connect to MQTT broker: %s", exc)
        logger.error("Check that Mosquitto is running and the host/port are correct.")
        raise SystemExit(1) from exc
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
