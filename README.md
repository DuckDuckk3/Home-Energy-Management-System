# HEMS — Milestone 1: MQTT telemetry prototype

This milestone runs a simulated household DC load telemetry stream through Mosquitto MQTT to a Python backend. All terminal instructions below use **Windows Command Prompt (CMD)**, not PowerShell.

## What is included

- `simulator`: publishes simulated voltage, current and power every 2 seconds.
- `backend`: subscribes to telemetry, validates JSON fields, and prints received messages.
- `mosquitto`: broker configuration and Docker Compose setup.
- `.env.example`: shared local configuration.
- `requirements.txt`: Python dependencies.

**Important:** the simulator generates synthetic data. It is not a measurement of a real household or PV system.

## Requirements

- Windows 10/11
- Python 3.11 or 3.12 recommended. Python 3.13 may also work, but this starter has not been specifically validated with it.
- One MQTT broker option:
  - Docker Desktop (recommended for this starter), or
  - Mosquitto installed locally

## 1. Extract and open the project

Extract the ZIP file. Open the project folder `hems_mqtt_milestone1` in File Explorer.

Click the address bar, type `cmd`, and press Enter. CMD should open in the project root. You can verify the location with:

```bat
cd
dir
```

The directory listing should include `backend`, `simulator`, `mosquitto`, and `requirements.txt`.

## 2. Create and activate a virtual environment

First, check which Python versions are installed:

```bat
py -0p
```

If Python 3.13 is installed, create the environment with:

```bat
py -3.13 -m venv .venv
```

Activate the environment in CMD:

```bat
.venv\Scripts\activate.bat
```

The command prompt should now begin with `(.venv)`.

Install the dependencies using the Python executable from the virtual environment:

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
**Important:** use `python -m pip` rather than a standalone `pip` command. This helps ensure packages are installed into the active virtual environment.

## 3. Start Mosquitto

Choose **one** of the following options. Do not start both brokers on the same port.

### Option A — Docker Compose

Make sure Docker Desktop is installed and running. In CMD, from the project root, run:

```bat
docker compose up -d
docker compose ps
```

The broker should listen on `127.0.0.1:1883` (localhost). This starter allows anonymous access for local development and binds the port to localhost only. Do not expose this configuration to a public network.

To view broker logs:

```bat
docker compose logs -f mosquitto
```

Press `Ctrl+C` to stop viewing logs. This does not stop the broker.

To stop the broker later:

```bat
docker compose down
```

If CMD says `docker` is not recognized, install Docker Desktop and ensure it is running, or use Option B.

### Option B — local Mosquitto installation

Install Mosquitto for Windows. From the project root, run:

```bat
mosquitto -c mosquitto\mosquitto.local.conf -v
```

Keep this CMD window open while testing. If `mosquitto` is not recognized, run `mosquitto.exe` using its full installation path or add its installation directory to `PATH`.

## 4. Start the backend

Open a **second CMD window** in the project root. Activate the environment:

```bat
.venv\Scripts\activate.bat
```

Then start the backend:

```bat
python -m backend.main
```
Expected startup output should indicate that the backend connected to MQTT and subscribed to:

```text
hems/v1/telemetry/#
```

Keep this window open.

## 5. Start the simulator

Open a **third CMD window** in the project root. Activate the environment:

```bat
.venv\Scripts\activate.bat
```

Start the periodic simulator:

```bat
python -m simulator.publisher
```

The simulator publishes one JSON message every 2 seconds. The backend CMD window should display the received telemetry.

Press `Ctrl+C` in the simulator window to stop publishing. Press `Ctrl+C` in the backend window to stop the backend.

## 6. Test one message without the periodic simulator

Keep the broker and backend running. Open another CMD window in the project root and run:

```bat
.venv\Scripts\activate.bat
python -m simulator.send_once
```

The backend should receive one test message. This checks the MQTT path separately from the periodic simulator.

## 7. Example payload

```json
{
  "schema_version": 1,
  "device_id": "sim-load-01",
  "source": "simulation",
  "timestamp": "2026-01-01T12:00:00+00:00",
  "voltage_v": 12.1,
  "current_a": 0.42,
  "power_w": 5.082
}
```

`power_w` is calculated as voltage multiplied by current in this synthetic example. The timestamp in actual output is generated at runtime.

## Troubleshooting

- **`No suitable Python runtime found`:** run `py -0p` and create the environment using an installed version listed by the launcher.
- **`Connection refused`:** ensure Mosquitto is running and `.env` uses `MQTT_HOST=127.0.0.1` and `MQTT_PORT=1883`.
- **Backend sees no data:** start the backend before the simulator; confirm both use the same `.env` and topic prefix.
- **Port 1883 already in use:** stop the other broker instance or change the port consistently in `.env`, `docker-compose.yml`, and the Mosquitto configuration.
- **`No module named paho`:** activate `.venv` and run `python -m pip install -r requirements.txt`.
- **`pip` launcher errors or packages install to the wrong Python:** use `.venv\Scripts\python.exe -m pip ...` to call the environment's Python directly.
- **`docker` is not recognized:** install and start Docker Desktop, or use Option B.
- **`Copy-Item` is not recognized:** that is a PowerShell command. In CMD, use `if not exist .env copy .env.example .env`.

## Project structure

```text
hems_mqtt_milestone1/
├── backend/
│   ├── __init__.py
│   └── main.py
├── simulator/
│   ├── __init__.py
│   ├── publisher.py
│   └── send_once.py
├── mosquitto/
│   ├── mosquitto.conf
│   └── mosquitto.local.conf
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Scope and limitations

This milestone does not yet include MySQL persistence, REST API, a Desktop UI, ML forecasting, Digital Twin logic, or real hardware control. Those are subsequent milestones. The current backend performs basic payload validation and console logging only.
