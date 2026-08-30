# IoT Monitoring Environmental

Este projeto monta uma stack completa de monitoramento ambiental IoT com 5 serviços Docker:

- Wokwi ESP32 (simulação com sensores)
- MQTT Broker — Eclipse Mosquitto 2
- Python bridge (MQTT → InfluxDB)
- InfluxDB 1.8 (base de dados temporal)
- Grafana 10.4.2 (10 painéis)
- Ping Monitor (latência de rede a um IP alvo)

Arquitetura em pipeline:

```
Wokwi ESP32 (DHT22 + PIR + Potenciômetro)
          │
          ▼ MQTT (harryspace/01/*)
     Mosquitto :1883 ──────────────────┐
          │                            │
          ▼                            ▼
      bridge.py                 ping_monitor.py
   (subscreve harryspace/+/+)   (publica harryspace/01/ping)
          │                            │
          └──────────────┬─────────────┘
                         ▼
                   InfluxDB :8086
                   (measurement: temperature, humidity, voltage,
                                 presence, ping, lux)
                         │
                         ▼
                   Grafana :3000
                   (Dashboard com 10 painéis)
```

## Estrutura do projeto

```text
iot-monitoring/
├── docker-compose.yml              # 5 serviços: mqtt, influxdb, grafana, bridge, ping-monitor
├── mosquitto.conf                  # Mosquitto: portas 1883 (MQTT) e 9001 (WebSocket)
├── requirements.txt                # paho-mqtt==1.6.1, influxdb==5.3.1
├── Dockerfile                      # Imagem para o serviço "bridge"
├── Dockerfile.ping                 # Imagem para o serviço "ping-monitor"
├── bridge.py                       # Bridge MQTT → InfluxDB
├── ping_monitor.py                 # Publica latência de ping no MQTT
├── publish_test_data.sh            # Script bash: publica valores de teste MQTT
├── README.md
├── wokwi/
│   ├── wokwi.ino                   # Firmware ESP32 (ANTES era referido como sketch.ino)
│   ├── diagram.json                # Circuito: ESP32 DevKit + DHT22 + PIR + Potenciômetro
│   ├── wokwi.toml                  # Config Wokwi (aponta para firmware pré-compilado em build/)
│   └── build/                      # Binários compilados do wokwi.ino (wokwi.ino.bin, etc.)
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── influxdb.yml        # DataSource InfluxDB (provisionamento automático)
│       └── dashboards/
│           ├── dashboard.yml       # Provider de dashboards
│           └── environmental-dashboard.json   # Dashboard (10 painéis)
└── .venv/                          # Ambiente virtual Python (opcional, para bridge.py local)
```

## Pré-requisitos

- Windows 10/11
- Docker Desktop instalado e em execução
- Python 3.8+ instalado (só se quiseres correr bridge.py fora do Docker)
- Git (opcional)

## Instalar Docker Desktop

1. Baixe em: https://www.docker.com/products/docker-desktop
2. Instale e reinicie o computador
3. Abra o Docker Desktop
4. Confirme que o ícone fica em execução (canto inferior direito)

## Instalar Python

No PowerShell:

```powershell
python --version
```

Se não existir, instale Python 3.8+ em:
https://www.python.org/downloads/windows/

## Criar ambiente virtual (opcional mas recomendado)

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
cd C:\Users\LENOVO\Projectos\iot-monitoring
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

Logs (individuais ou todos):

```powershell
docker compose logs mosquitto
docker compose logs influxdb
docker compose logs grafana
docker compose logs bridge
docker compose logs ping-monitor
docker compose logs -f bridge    # follow (a tempo real)
```

Parar tudo:

```powershell
docker compose down
```

## Verificar portas

| Serviço | Porta | URL / destino |
|---|---|---|
| Mosquitto MQTT | 1883 | `0.0.0.0:1883` (qualquer interface) |
| Mosquitto WebSocket | 9001 | `0.0.0.0:9001` |
| InfluxDB | 8086 | http://localhost:8086/ping |
| Grafana | 3000 | http://localhost:3000 |

## Ping Monitor (serviço 5 do docker-compose)

O `ping-monitor` faz ping a um IP (ex: switch/router) e publica a latência em `harryspace/[LOCATION]/ping` (em ms). Por defeito:

```
SWITCH_IP=192.168.1.1
LOCATION=01
PING_INTERVAL=5 (segundos)
```

Para alterar (ex: o teu router está em 192.168.1.254), edita as `environment` do serviço `ping-monitor` no [docker-compose.yml](docker-compose.yml) e faz:

```powershell
docker compose up -d --build ping-monitor
```

Valores publicados:
- Latência (float) em ms, se sucesso
- `-1`, se o alvo for inalcançável

## Wokwi e comunicação MQTT

### Diferença importante entre "localhost"

- `localhost` **no teu computador** = o próprio Windows
- `localhost` **dentro da simulação Wokwi** = a própria VM/simulador do Wokwi (na cloud deles), NÃO o teu PC
- Por isso, Wokwi **não** deve apontar para `localhost` para chegar ao Mosquitto do teu Docker.

### Duas opções válidas para MQTT_HOST no wokwi.ino

No ficheiro [wokwi/wokwi.ino](wokwi/wokwi.ino) linhas 12-18, o firmware usa:

```cpp
#ifndef MQTT_HOST
#define MQTT_HOST "host.wokwi.internal"
#endif
```

#### Opção A — Wokwi Private IoT Gateway (default no código)

`host.wokwi.internal` é um **hostname especial do Wokwi** que resolve automaticamente para a tua máquina Windows **se estiveres a usar a funcionalidade paga "Wokwi Private IoT Gateway"**.

- Vantagem: não precisas de saber o teu IP LAN nem abrir firewall.
- Desvantagem: requer subscrição Wokwi paga; **não funciona com Wokwi free/standard**.

#### Opção B — IP da máquina Windows na LAN (Wokwi free/standard)

Usa o **IPv4 da tua interface de rede ativa**. Funciona com Wokwi free, mas precisas de abrir a porta 1883 no firewall.

Como descobrir o IP no Windows:

```powershell
ipconfig
```

Procura a interface ativa (Wi-Fi ou Ethernet):

```text
IPv4 Address . . . . . . . . . : 192.168.1.42
```

Edita o [wokwi/wokwi.ino](wokwi/wokwi.ino) e usa esse IP:

```cpp
// Ou define diretamente (substitui o #ifndef acima)
#define MQTT_HOST "192.168.1.42"
```

**Firewall do Windows:** se a conexão falhar, liberta a porta 1883:
- Windows Defender Firewall → Regras de entrada → Nova regra
- Tipo = Porta → TCP 1883 → Permitir a ligação
- Ou permite "Docker Desktop Backend" e o processo `mosquitto` nas regras de saída/entrada.

## Wokwi setup (simulação do ESP32)

### Sensores no circuito (conferidos em diagram.json)

| Sensor | Pin no ESP32 | Publica em MQTT | Measurement no InfluxDB |
|---|---|---|---|
| **DHT22** (temperatura + humidade) | SDA = GPIO 13 | `harryspace/01/temperature`, `harryspace/01/humidity` | `temperature`, `humidity` |
| **PIR** (sensor de presença/movimento) | OUT = GPIO 27 | `harryspace/01/presence` (0 = sem movimento, 1 = detetado) | `presence` |
| **Potenciômetro** (tensão 0–3.3 V) | SIG = GPIO 34 | `harryspace/01/voltage` (0.0–3.3 V) | `voltage` |

> **Nota:** Não existe LDR neste circuito. O painel de "lux" foi removido da dashboard; o bridge.py ainda aceita `lux` por retrocompatibilidade, mas não há sensor a publicá-lo.

### Passos no Wokwi Web

1. Acede https://wokwi.com
2. Cria um novo projeto ESP32 (ESP32 DevKit C V4)
3. Adiciona os sensores exatos do diagrama:
   - 1× **DHT22** (temperatura + humidade)
   - 1× **PIR Motion Sensor** (presença/movimento)
   - 1× **Potenciômetro**
4. Abre o arquivo de diagrama e cola o conteúdo de [wokwi/diagram.json](wokwi/diagram.json)
5. No separador do sketch, substitui pelo conteúdo de [wokwi/wokwi.ino](wokwi/wokwi.ino)
6. Ajusta `MQTT_HOST` conforme a secção anterior (Opção A ou B)
7. Clica em **Start the Simulation** (botão verde)

O firmware publica automaticamente a cada 5 segundos, com logs detalhados na Serial Wokwi a 115200 baud.

## MQTT manual (testes rápidos)

Para testar sem Wokwi, usa um cliente MQTT como **MQTT Explorer** ou os comandos `mosquitto_pub` (disponíveis no container mosquitto).

- Host: `localhost` (ou IP LAN, para clientes externos ao Docker)
- Port: `1883`
- Sem autenticação (anonymous = true)

### Publicar mensagens de exemplo

Tópicos e formatos reconhecidos pelo [bridge.py](bridge.py) (linha 18, `VALID_MEASUREMENTS`):

```
harryspace/[LOCATION]/temperature   →  float (ex: 24.5, °C)
harryspace/[LOCATION]/humidity      →  float (ex: 58.0, %)
harryspace/[LOCATION]/voltage       →  float (ex: 3.28, V)
harryspace/[LOCATION]/presence      →  0 ou 1 (PIR)
harryspace/[LOCATION]/ping          →  float (ex: 12.4, ms, ou -1 se unreachable)
harryspace/[LOCATION]/lux           →  float (sem sensor associado, retrocompatibilidade)
```

Exemplos (dentro do container mosquitto, ou com mosquitto-clients instalado):

```bash
# Temperatura
mosquitto_pub -h localhost -p 1883 -t "harryspace/01/temperature" -m "24.5"
# Humidade
mosquitto_pub -h localhost -p 1883 -t "harryspace/01/humidity"    -m "58.0"
# Presença PIR (0 = n detetado, 1 = detetado)
mosquitto_pub -h localhost -p 1883 -t "harryspace/01/presence"    -m "1"
# Tensão Potenciômetro (0.0 a 3.3 V)
mosquitto_pub -h localhost -p 1883 -t "harryspace/01/voltage"     -m "3.28"
# Ping (ms, ou -1 se unreachable)
mosquitto_pub -h localhost -p 1883 -t "harryspace/01/ping"        -m "12.4"
```

Depois confirma nos logs do bridge:

```powershell
docker compose logs --tail=20 bridge
```

Esperado (exemplo):
```text
[MQTT] Received: harryspace/01/temperature = 24.5
[INFLUXDB] Saved: temperature = 24.5 location=01
```

Também podes correr o script [publish_test_data.sh](publish_test_data.sh) (bash, requer `mosquitto-clients`):
```bash
./publish_test_data.sh
```

## Grafana

Acede a:

```text
http://localhost:3000
```

Login por defeito (podes alterar depois):
- Usuário: `admin`
- Senha:   `admin`

### Provisionamento automático

- **DataSource InfluxDB** configurado via [grafana/provisioning/datasources/influxdb.yml](grafana/provisioning/datasources/influxdb.yml)
  - URL: `http://influxdb:8086` (nome do serviço Docker, resolve internamente)
  - Database: `harryspace` | user: `user` | password: `password`
  - `isDefault: true`

- **Dashboard "Monitoramento Ambiental"** carregado via [grafana/provisioning/dashboards/environmental-dashboard.json](grafana/provisioning/dashboards/environmental-dashboard.json)
  - 10 painéis no total:
    - **Timeseries (5):** Temperatura (°C), Humidade (%), Presença (PIR, 0/1), Tensão (V), Ping ao Switch (ms)
    - **Stat (5):** Temperatura Atual, Humidade Atual, Presença Atual, Tensão Atual, Ping Atual
  - Template variable `location = "01"` (constante, escondida)
  - Refresh automático a cada 10 s
  - Janela temporal padrão: últimos 5 minutos (`now-5m` até `now`)

### Resolução de problemas do Grafana

- **Painéis brancos / sem dados:** Confirma primeiro que o bridge está a receber e guardar (ver `docker compose logs bridge`). Depois, dentro do Grafana:
  1. Abre Connections → Data sources → InfluxDB
  2. Clica em **Test** (canto inferior direito). Tem de mostrar "Data source is working".
- **Datasource aparece mas erros nas queries:** Vai ao painel de Admin → Server Admin → Data sources, e garante que o UID do datasource corresponde ao esperado pelo JSON da dashboard.
- **Dados antigos não aparecem:** Aumenta a janela temporal (canto superior direito, ex: `Last 24 hours`).

## Verificação direta no InfluxDB

Para consultar diretamente a base de dados `harrydb` é `harryspace`:

Opção 1 — CLI dentro do container influxdb:
```powershell
docker compose exec influxdb influx -database harryspace -execute "SHOW MEASUREMENTS"
docker compose exec influxdb influx -database harryspace -execute "SELECT * FROM temperature ORDER BY time DESC LIMIT 10"
```

Opção 2 — HTTP API (curl / Postman):
```bash
curl -G 'http://localhost:8086/query?db=harryspace' --data-urlencode 'q=SHOW MEASUREMENTS'
curl -G 'http://localhost:8086/query?db=harryspace' --data-urlencode 'q=SELECT last(value), location FROM temperature GROUP BY location'
```

Medições esperadas (se todos os publicadores estiverem a funcionar):
- `temperature` — DHT22
- `humidity` — DHT22
- `voltage` — Potenciômetro ESP32
- `presence` — PIR ESP32
- `ping` — ping_monitor.py

## Troubleshooting rápido

### Docker não inicia
```powershell
docker ps
```
Se falhar, inicia o Docker Desktop e espera 1–2 minutos até o daemon ficar "running".

### Containers não sobem
```powershell
docker compose config        # valida sintaxe do compose
docker compose up -d --build # força rebuild das imagens bridge e ping-monitor
```

### Bridge não conecta ao Mosquitto / não conecta ao InfluxDB
```powershell
docker compose logs bridge --tail=50
docker compose ps   # confere que mqtt e influxdb estão healthy
```
Os healthchecks garantem que bridge só arranca depois de MQTT e InfluxDB responderem. Se ainda assim falhar, verifica nomes DNS (MQTT_BROKER=`mqtt`, INFLUX_HOST=`influxdb`) — os containers Docker resolvem estes nomes automaticamente pela rede interna `iot-monitoring_default`.

### Wokwi não conecta ao broker MQTT
1. Confirmar IP do PC (ipconfig) e que é o mesmo em `MQTT_HOST` do wokwi.ino
2. Confirmar que Mosquitto está a ouvir em `0.0.0.0:1883` (ver [mosquitto.conf](mosquitto.conf) linha 5 e `netstat -an | Select-String :1883`)
3. Confirmar firewall do Windows com regra de entrada TCP 1883 permitida
4. Testar conexão externamente com MQTT Explorer de outro dispositivo na mesma LAN

### Ping Monitor publica sempre -1 (unreachable)
O container `ping-monitor` corre a partir da **rede Docker interna**. Se `SWITCH_IP` for um IP privado (ex: 192.168.x.x), o Docker precisa de ter rota para essa LAN. No Docker Desktop em Windows com WSL2 isto funciona por defeito com NAT; se não funcionar, troca `SWITCH_IP` para um IP público (ex: 8.8.8.8) apenas para testar.

### Grafana não vê a fonte / datasource "InfluxDB"
Acede a http://localhost:3000 → Configuration → Data sources, confirma:
- Nome = `InfluxDB`
- URL = `http://influxdb:8086` (não localhost!)
- Database = `harryspace`
- User / Password = `user` / `password`
- Carrega em "Save & test"

## Observações finais

Arquitetura completa solicitada:
```
Wokwi ESP32 (DHT22+PIR+Pot) → MQTT → Mosquitto :1883 → bridge.py → InfluxDB :8086 → Grafana :3000
                                                              ↑
                                                   ping_monitor.py (publica ping)
```

O Docker Desktop/daemon precisa estar sempre ativo para os 5 serviços (mqtt, influxdb, grafana, bridge, ping-monitor) funcionarem. Se só quiseres testar o bridge localmente (fora do Docker), desativa o serviço `bridge` do compose e corre `python bridge.py` — não te esqueças de ativar o venv e instalar o requirements.txt.
