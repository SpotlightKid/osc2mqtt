#!/bin/bash
#
# start osc2mqtt.py OSC to MQTT bridge with proper hosts and ports
#

MQTT_HOST="localhost"
MQTT_PORT="1883"
OSC_PORT="9001"

PYTHONPATH=$(pwd) python -m osc2mqtt -m $MQTT_HOST:$MQTT_PORT -p $OSC_PORT "$@"
