#!/bin/bash
#
# start osc2mqtt.py OSC to MQQT bridge with proper hosts and ports
#

MQTT_HOST="dockstar3"
MQTT_PORT="1883"
OSC_PORT="9001"

python osc2mqtt.py -m $MQTT_HOST:$MQTT_PORT -p $OSC_PORT "$@"
