#!/bin/bash
# InfluxDB init script — creates 90-day retention policy for harryspace database
# This script runs automatically when the InfluxDB container starts for the first time

set -e

echo "==> Creating 90-day retention policy for harryspace database..."

influx -execute "CREATE RETENTION POLICY \"ninety_days\" ON \"harryspace\" DURATION 90d REPLICATION 1 DEFAULT"

echo "==> Retention policy 'ninety_days' created (90 days, default)"
