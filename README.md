# HEMS — Milestone 1: MQTT telemetry prototype

This milestone runs a simulated household DC load telemetry stream through Mosquitto MQTT to a Python backend.

## What is included

- `simulator`: publishes simulated voltage, current and power every 2 seconds.
- `backend`: subscribes to telemetry, validates JSON fields, and prints received messages.
- `mosquitto`: broker configuration and Docker Compose setup.
- `.env.example`: shared local configuration.
- `requirements.txt`: Python dependencies.

**Important:** the simulator generates synthetic data. It is not a measurement of a real household or PV system.

## Requirements

- Windows 10/11
- Python 3.11 or 3.12 recommended
- One MQTT broker option:
  - Docker Desktop (recommended for this starter), or
  - Mosquitto installed locally

## 1. Extract and open the project

Extract the ZIP file, then open PowerShell in the `hems_mqtt_milestone1` folder.

## 2. Create a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If Python 3.12 is not installed, use `py -3.11` instead.

## 3. Start Mosquitto

### Option A — Docker Compose

Make sure Docker Desktop is running, then:

```powershell
docker compose up -d
docker compose ps
```

The broker listens on `localhost:1883`. This starter binds the port to localhost only and enables anonymous access for local development. Do not expose this configuration to a public network.

View broker logs:

```powershell
docker compose logs -f mosquitto
```

Stop it later with:

```powershell
docker compose down
```

### Option B — local Mosquitto installation

Install Mosquitto for Windows, then start the broker with this project's config file. From the project root, run:

```powershell
mosquitto -c .\mosquitto\mosquitto.local.conf -v
```

If `mosquitto` is not recognized, use the full path to `mosquitto.exe` or add its installation directory to PATH.

Do not start both broker options on the same port at the same time.

## 4. Start the backend

Open a **new PowerShell terminal** in the project root, activate the environment if needed, then run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m backend.main
```

Expected startup output includes a message that the backend connected to MQTT and subscribed to `hems/v1/telemetry/#`.

## 5. Start the simulator

Open another **new PowerShell terminal** in the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m simulator.publisher
```

The simulator publishes one JSON message every 2 seconds. The backend terminal should display the received data.

Press `Ctrl+C` in each terminal to stop the process.

## 6. Test the message format without the simulator

With the broker and backend running, open a third terminal and run:

```powershell
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

`power_w` is calculated as voltage × current in this synthetic example. The timestamp in actual output is generated at runtime.

## Troubleshooting

- **Connection refused:** ensure Mosquitto is running and `.env` uses `MQTT_HOST=127.0.0.1`, `MQTT_PORT=1883`.
- **Backend sees no data:** start the backend before the simulator; check that both use the same `.env` and topic prefix.
- **Port 1883 already in use:** stop the other broker instance or change the port consistently in `.env`, `docker-compose.yml`, and `mosquitto/mosquitto.conf`.
- **`No module named paho`:** activate the virtual environment and run `pip install -r requirements.txt`.
- **No Docker:** use Option B to install and start Mosquitto locally.

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
