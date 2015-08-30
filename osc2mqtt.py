#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bridge bewteen OSC and MQTT."""

from __future__ import print_function, unicode_literals

import argparse
import ipaddress
import json
import logging
import sys
import time

import liblo

import paho.mqtt.client as mqtt


log = logging.getLogger('osc2mqtt')


def handle_osc(oscaddr, values, types, clientaddr, userdata):
    log.debug("OSC recv: %s %r", oscaddr, values)
    if len(values) > 1:
        msg = json.dumps(values)
    else:
        msg = values[0]
    topic = userdata['prefix'] + oscaddr
    log.debug("MQTT publish: %s %s", topic, msg)
    userdata['mqtt'].publish(topic, msg)


def on_connect(client, userdata, flags, rc):
    log.debug("MQTT connect: %s", mqtt.connack_string(rc))
    client.subscribe('#')


def on_disconnect(client, userdata, rc):
    log.debug("MQTT disconnect: %s", mqtt.error_string(rc))


def on_message(client, userdata, msg):
    log.debug("MQTT recv: %s %r", msg.topic, msg.payload)
    if userdata.get('osc_receiver'):
        try:
            values = json.loads(msg.payload.decode('utf-8'))
        except (TypeError, ValueError):
            values = [msg.payload]

        if isinstance(values, (int, float)):
            values = [values]

        addr = '/' + msg.topic.lstrip(userdata.get('prefix', '')).lstrip('/')
        log.debug("OSC send: %s %r", addr, values)
        userdata['osc'].send(userdata['osc_receiver'], addr, *values)


def parse_hostport(addr, port=9000):
    if ('::' in addr and ']:' in addr) or ('::' not in addr and ':' in addr):
        host, port = addr.rsplit(':', 1)
    else:
        host = addr

    if host.startswith('[') and host.endswith(']'):
        host = host[1:-1]

    return (host, int(port))


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        '-p', '--osc-port',
        type=int,
        metavar='PORT',
        default=9001,
        help="Local OSC server (UDP) port (default: %(default)s)")
    ap.add_argument(
        '-m', '--mqtt-broker',
        metavar='ADDR[:PORT]',
        default='localhost:1883',
        help="MQTT broker addr[:port] (default: %(default)s)")
    ap.add_argument(
        '-o', '--osc-receiver',
        metavar='ADDR[:PORT]',
        help='Also bridge MQTT to OSC receiver addr[:port] via UDP '
             '(default: one-way)')
    ap.add_argument(
        '-t', '--topic-prefix',
        default='',
        metavar='PREFIX',
        help='MQTT topic prefix to prepend to/strip from OSC addresses')
    ap.add_argument(
        '-v', '--verbose',
        action="store_true",
        help='Enable verbose logging')

    args = ap.parse_args(args if args is not None else sys.argv[1:])

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    userdata = {'prefix': args.topic_prefix}

    if args.osc_receiver:
        osc_host, osc_port = parse_hostport(args.osc_receiver, 9000)
        userdata['osc_receiver'] = liblo.Address(osc_host, osc_port, liblo.UDP)

    mqttclient = mqtt.Client("osc2mqtt", userdata=userdata)
    userdata['mqtt'] = mqttclient
    mqttclient.on_connect = on_connect
    mqttclient.on_disconnect = on_disconnect
    mqttclient.on_message = on_message
    oscserver = liblo.ServerThread(args.osc_port)
    userdata['osc'] = oscserver
    oscserver.add_method(None, None, handle_osc, userdata)

    mqtt_host, mqtt_port = parse_hostport(args.mqtt_broker, 1883)
    log.info("Connecting to MQTT broker %s:%s ...", mqtt_host, mqtt_port)
    mqttclient.connect(mqtt_host, mqtt_port)

    log.debug("Starting MQTT thread...")
    mqttclient.loop_start()

    log.info("Starting OSC server listening on port %s ...", args.osc_port)
    oscserver.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Interrupted.")
    finally:
        log.info("Stopping OSC server ...")
        oscserver.stop()
        log.debug("Stopping MQTT thread ...")
        mqttclient.loop_stop()
        log.info("Disconnecting from MQTT broker ...")
        mqttclient.disconnect()
        log.info("Done.")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
