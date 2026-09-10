# IoT Monitoring System

**Professional environmental monitoring system with real-time telemetry, MQTT integration, time-series storage, and visualization.**

A complete IoT monitoring stack demonstrating:
- Edge device simulation (ESP32 with DHT22, PIR, Potentiometer sensors)
- MQTT message broker
- Python microservices (Bridge, Ping Monitor)
- Time-series data persistence (InfluxDB)
- Real-time visualization (Grafana)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ESP32 Wokwi Simulation                                │
│  ├─ DHT22: Temperature + Humidity                       │
│  ├─ PIR: Motion Detection                              │
│  └─ Potentiometer: Analog Voltage                       │
│                                                         │
│  MQTT Topics:                                           │
│  harryspace/01/{temperature,humidity,presence,voltage} │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │ WiFi + MQTT
                   ▼
         ┌─────────────────────┐
         │  Mosquitto Broker   │
         │   :1883, :9001      │
         └──────┬──────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
  Bridge   Ping Monitor  (local dev)
    │           │
    └───────────┼───────────┘
                ▼
        ┌──────────────────┐
        │  InfluxDB 1.8    │
        │  :8086           │
        │  harryspace DB   │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │  Grafana 10.4.2  │
        │  :3000           │
        │  10 Panels       │
        └──────────────────┘
```

## Technologies

- **ESP32**: Microcontroller with WiFi (simulated in Wokwi)
- **MQTT**: Message broker (Eclipse Mosquitto)
- **Python 3.11**: Services (Bridge, Ping Monitor)
- **InfluxDB 1.8**: Time-series database
- **Grafana 10.4.2**: Data visualization
- **Docker Compose**: Orchestration

## Project Structure

```
iot-monitoring/
│
├── .env.example                    # Configuration template (no secrets)
├── .gitignore                      # Git ignore rules
├── docker-compose.yml              # 5 services: mqtt, influxdb, grafana, bridge, ping-monitor
├── requirements.txt                # Python dependencies + pytest
├── pytest.ini                      # Test configuration
├── README.md                       # This file
│
├── infrastructure/                 # Non-code infrastructure configs
│   ├── mosquitto/
│   │   └── mosquitto.conf
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── influxdb.yml
│           └── dashboards/
│               ├── dashboard.yml
│               └── environmental-dashboard.json
│
├── services/                       # Microservices
│   ├── bridge/                     # MQTT → InfluxDB bridge
│   │   ├── Dockerfile
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── models.py
│   │   │   ├── mqtt_handler.py
│   │   │   ├── influx_client.py
│   │   │   ├── telemetry_service.py
│   │   │   └── logger_config.py
│   │   └── tests/
│   │       ├── test_models.py
│   │       └── test_config.py
│   │
│   └── ping_monitor/               # Network latency monitoring
│       ├── Dockerfile
│       ├── src/
│       │   ├── main.py
│       │   ├── config.py
│       │   ├── mqtt_client.py
│       │   ├── ping_service.py
│       │   └── logger_config.py
│       └── tests/
│
├── wokwi/                          # ESP32 Simulation (Wokwi)
│   ├── wokwi.ino                   # Firmware source
│   ├── diagram.json                # Circuit diagram
│   ├── wokwi.toml                  # Configuration
│   └── build/                      # Compiled binaries
│
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md             # System design & data flow
│   ├── MQTT_TOPICS.md              # Message protocol specification
│   ├── SETUP.md                    # Installation & configuration
│   └── TROUBLESHOOTING.md          # Common issues & solutions
│
├── scripts/                        # Utility scripts
│   ├── publish_test_data.sh        # MQTT test publisher
│   └── setup_env.sh                # Environment setup helper
│
└── tests/                          # Integration tests (future)
```

## Prerequisites

- **Docker Desktop** (Windows 10/11, macOS, Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Docker Compose included
- **Python 3.8+** (optional, for local development)
- **Git** (optional, for version control)

## Quick Start

### 1. Configure Environment

```bash
# Copy configuration template
cp .env.example .env

# Edit .env with your settings (change default passwords!)
```

### 2. Start Services

```bash
# Start all 5 services
docker compose up -d

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Instalar dependências Python (só para bridge.py local)

```powershell
pip install -r requirements.txt
```

## Iniciar serviços Docker (recomendado)

No PowerShell, dentro da pasta do projeto:

```powershell
docker compose up -d --build
```

Isto arranca **os 5 serviços** com healthchecks:
1. `mqtt` (Mosquitto, porta 1883 + 9001)
2. `influxdb` (InfluxDB 1.8, porta 8086) — cria DB `harryspace` automaticamente
3. `grafana` (Grafana 10.4.2, porta 3000) — espera influxdb saudável
4. `bridge` (Python, bridge MQTT → InfluxDB) — espera mqtt + influxdb saudáveis
5. `ping-monitor` (Python, publica latência de ping) — espera mqtt saudável

Verificar containers em execução:

```powershell
docker compose ps
```

Expected output: all 5 services showing `Up` status.

### 3. Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / (from .env) |
| **InfluxDB API** | http://localhost:8086 | — |
| **Mosquitto MQTT** | localhost:1883 | — |

### 4. View Logs

```bash
# Bridge service logs
docker compose logs bridge --tail 50

# All services (real-time)
docker compose logs -f
```

### 5. Stop Services

```bash
docker compose down
```

## Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# MQTT Configuration
MQTT_BROKER=mqtt              # Broker hostname
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# InfluxDB Configuration
INFLUX_HOST=influxdb
INFLUX_PORT=8086
INFLUX_DB=harryspace
INFLUX_USER=user
INFLUX_PASSWORD=password      # ⚠️ CHANGE THIS IN PRODUCTION

# Grafana Configuration
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin   # ⚠️ CHANGE THIS IN PRODUCTION

# Services Configuration
LOCATION=01
LOG_LEVEL=INFO
SWITCH_IP=192.168.1.1
PING_INTERVAL=5
```

## MQTT Topics

Current topics published by Wokwi ESP32:

```
harryspace/01/temperature   → Temperature (°C)
harryspace/01/humidity      → Humidity (%)
harryspace/01/presence      → Motion (0/1)
harryspace/01/voltage       → Voltage (0-3.3V)
harryspace/01/ping          → Latency (ms)
```

See `docs/MQTT_TOPICS.md` for detailed specification.

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest services/bridge/tests/test_models.py -v

# With coverage report
pytest --cov=services/bridge/src tests/
```

## Local Development

To run services locally without Docker:

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Services

```bash
# Bridge (requires MQTT and InfluxDB running)
python services/bridge/src/main.py

# Ping Monitor
python services/ping_monitor/src/main.py
```

## Troubleshooting

See `docs/TROUBLESHOOTING.md` for:
- Services won't start
- MQTT connection issues
- InfluxDB initialization
- Grafana data display problems
- Ping Monitor troubleshooting

## Documentation

- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **MQTT Protocol:** [docs/MQTT_TOPICS.md](docs/MQTT_TOPICS.md)
- **Setup Guide:** [docs/SETUP.md](docs/SETUP.md)
- **Troubleshooting:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Key Features

✅ **Modular Architecture** - Clear separation of concerns  
✅ **Secure Configuration** - Environment-based secrets  
✅ **Comprehensive Logging** - Structured logs per module  
✅ **Error Handling** - Graceful reconnection logic  
✅ **Testing** - Unit tests and coverage reporting  
✅ **Professional Documentation** - Complete guides

## License

[To be determined by project owner]
