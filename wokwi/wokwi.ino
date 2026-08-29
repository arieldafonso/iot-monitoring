#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 13
#define DHTTYPE DHT22

#define PIR_PIN 27
#define POT_PIN 34

// Wokwi Private IoT Gateway
#ifndef MQTT_HOST
#define MQTT_HOST "host.wokwi.internal"
#endif

#ifndef MQTT_PORT
#define MQTT_PORT 1883
#endif

const char* ssid = "Wokwi-GUEST";
const char* password = "";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// =====================================================
// CALLBACK MQTT
// =====================================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {

  Serial.println();
  Serial.println("========== MQTT RECEBIDO ==========");

  Serial.print("Topic: ");
  Serial.println(topic);

  Serial.print("Mensagem: ");

  for (unsigned int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }

  Serial.println();
  Serial.println("===================================");
  Serial.println();
}

// =====================================================
// CONVERSÃO POTENCIÔMETRO → VOLTAGEM
// =====================================================

float readPotVoltage(int adcValue) {

  return (adcValue / 4095.0f) * 3.3f;
}

// =====================================================
// CONEXÃO WIFI
// =====================================================

void connectWiFi() {

  Serial.println();
  Serial.println("===================================");
  Serial.println("         CONEXÃO WIFI");
  Serial.println("===================================");

  Serial.print("SSID: ");
  Serial.println(ssid);

  Serial.println("Connecting to WiFi...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");

  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  Serial.println("===================================");
  Serial.println();
}

// =====================================================
// CONEXÃO MQTT
// =====================================================

void reconnectMQTT() {

  while (!client.connected()) {

    Serial.println();
    Serial.println("===================================");
    Serial.println("         CONEXÃO MQTT");
    Serial.println("===================================");

    Serial.print("Broker: ");
    Serial.println(MQTT_HOST);

    Serial.print("Porta: ");
    Serial.println(MQTT_PORT);

    Serial.print("Connecting MQTT...");

    if (client.connect("esp32-harryspace")) {

      Serial.println();
      Serial.println("MQTT connected");

      if (client.subscribe("harryspace/01/+")) {

        Serial.println("MQTT subscription OK");
        Serial.println("Subscribed: harryspace/01/+");

      } else {

        Serial.println("ERRO ao subscrever MQTT");
      }

      Serial.println("===================================");
      Serial.println();

    } else {

      Serial.println();
      Serial.print("MQTT connection failed, rc=");
      Serial.println(client.state());

      Serial.println("Retrying in 5 seconds...");

      delay(5000);
    }
  }
}

// =====================================================
// PUBLICAR DADOS MQTT
// =====================================================

void publishReading(const char* topic, float value) {

  char payload[32];

  dtostrf(value, 1, 2, payload);

  Serial.println();
  Serial.println("------------- MQTT PUBLISH -------------");

  Serial.print("Topic: ");
  Serial.println(topic);

  Serial.print("Payload: ");
  Serial.println(payload);

  bool result = client.publish(topic, payload);

  if (result) {

    Serial.println("Status: PUBLICADO COM SUCESSO");

  } else {

    Serial.println("Status: ERRO AO PUBLICAR");
  }

  Serial.println("----------------------------------------");
}

// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("=======================================");
  Serial.println("   IoT ENVIRONMENTAL MONITORING");
  Serial.println("=======================================");
  Serial.println("ESP32 iniciado");
  Serial.println("=======================================");
  Serial.println();

  dht.begin();

  // PIR como entrada digital
  pinMode(PIR_PIN, INPUT);

  // Configuração MQTT
  client.setServer(MQTT_HOST, MQTT_PORT);
  client.setCallback(mqttCallback);

  // Conecta WiFi
  connectWiFi();
}

// =====================================================
// LOOP
// =====================================================

void loop() {

  // Verifica WiFi
  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi desconectado.");

    connectWiFi();
  }

  // Verifica MQTT
  if (!client.connected()) {

    reconnectMQTT();
  }

  client.loop();

  // ===================================================
  // LEITURA DOS SENSORES
  // ===================================================

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  int potRaw = analogRead(POT_PIN);

  float voltage = readPotVoltage(potRaw);

  // PIR
  int pirState = digitalRead(PIR_PIN);

  // ===================================================
  // CONSOLE
  // ===================================================

  Serial.println();
  Serial.println("=======================================");
  Serial.println("        LEITURA DOS SENSORES");
  Serial.println("=======================================");

  // ===================================================
  // TEMPERATURA
  // ===================================================

  if (!isnan(temperature)) {

    Serial.print("Temperatura: ");
    Serial.print(temperature);
    Serial.println(" °C");

    publishReading(
      "harryspace/01/temperature",
      temperature
    );

  } else {

    Serial.println("Temperatura: ERRO");
  }

  // ===================================================
  // HUMIDADE
  // ===================================================

  if (!isnan(humidity)) {

    Serial.print("Umidade: ");
    Serial.print(humidity);
    Serial.println(" %");

    publishReading(
      "harryspace/01/humidity",
      humidity
    );

  } else {

    Serial.println("Umidade: ERRO");
  }

  // ===================================================
  // PRESENÇA / MOVIMENTO
  // ===================================================

  Serial.print("Presença: ");

  if (pirState == HIGH) {

    Serial.println("DETECTADA");

  } else {

    Serial.println("NÃO DETECTADA");
  }

  publishReading(
    "harryspace/01/presence",
    pirState
  );

  // ===================================================
  // POTENCIÔMETRO
  // ===================================================

  Serial.print("Potenciômetro ADC: ");
  Serial.println(potRaw);

  Serial.print("Voltagem: ");
  Serial.print(voltage);
  Serial.println(" V");

  publishReading(
    "harryspace/01/voltage",
    voltage
  );

  // ===================================================

  Serial.println();
  Serial.println("Próxima leitura em 5 segundos...");
  Serial.println("=======================================");
  Serial.println();

  delay(5000);
}