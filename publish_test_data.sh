#!/bin/bash
# Publica valores de teste para todas as métricas da dashboard harryspace/01
# Uso: ./publish_test_data.sh  (dentro da VM, com mosquitto-clients instalado)

BROKER="localhost"
PORT="1883"
LOCATION="01"

echo "Publicando temperatura..."
mosquitto_pub -h "$BROKER" -p "$PORT" -t "harryspace/$LOCATION/temperature" -m "24.5"

echo "Publicando humidade..."
mosquitto_pub -h "$BROKER" -p "$PORT" -t "harryspace/$LOCATION/humidity" -m "58.0"

echo "Publicando luminosidade..."
mosquitto_pub -h "$BROKER" -p "$PORT" -t "harryspace/$LOCATION/lux" -m "850"

echo "Publicando tensão..."
mosquitto_pub -h "$BROKER" -p "$PORT" -t "harryspace/$LOCATION/voltage" -m "3.28"

echo "Publicando ping..."
mosquitto_pub -h "$BROKER" -p "$PORT" -t "harryspace/$LOCATION/ping" -m "12.4"

echo "Feito. Confirma com: docker compose logs --tail=20 bridge"
