#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bridge between OSC and MQTT."""

from __future__ import absolute_import, unicode_literals

import argparse
import logging
import shlex
import sys
import time

from collections import OrderedDict

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import liblo
import paho.mqtt.client as mqtt

from .converter import Osc2MqttConverter, ConversionRule
from .util import as_bool, parse_hostport, parse_list


log = logging.getLogger('osc2mqtt')


def read_config(fn, options="options"):
    config = {'rules': OrderedDict()}
    defaults = dict(
        match = '^/?(.*)',
        address = r'/\1',
        topic = r'\1',
        type = 'struct',
        format = 'B',
        from_mqtt = None,
        from_osc = None,
        osctags = None
    )

    if fn:
        cp = configparser.RawConfigParser(defaults)
        cp.read(fn)
        if cp.has_section(options):
            config.update(i for i in cp.items(options)
                          if i not in cp.items('DEFAULT'))

        for section in cp.sections():
            if section.startswith(':'):
                name = section[1:]
                config['rules'][name] = dict(cp.items(section))

    subscriptions = parse_list(config.get('subscriptions', '#'))
    config['subscriptions'] = []
    encode = ((lambda s: s.encode('utf-8'))
              if isinstance(b'', str) else (lambda s: s))
    for sub in subscriptions:
        config['subscriptions'].append((encode(sub), 0))

    return config


class Osc2MqttBridge(object):
    def __init__(self, config, converter):
        """Setup OSC and MQTT servers.

        @param config: configuration directory
        @param converter: Osc2MqttConverter instance

        """
        self.converter = converter
        self.config = config
        self.mqtt_host, self.mqtt_port = parse_hostport(
            config.get("mqtt_broker", "localhost"), 1883)
        self.osc_port = int(config.get("osc_port", 9001))
        self.osc_receiver = config.get("osc_receiver")
        self.subscriptions = config.get("subscriptions", ['#'])

        if self.osc_receiver:
            host, port = parse_hostport(self.osc_receiver, 9000)
            self.osc_receiver = liblo.Address(host, port, liblo.UDP)

        self.mqttclient = mqtt.Client(config.get("client_id", "osc2mqtt"))
        self.mqttclient.on_connect = self.mqtt_connect
        self.mqttclient.on_disconnect = self.mqtt_disconnect
        self.mqttclient.on_message = self.handle_mqtt

        self.oscserver = liblo.ServerThread(self.osc_port)
        self.oscserver.add_method(None, None, self.handle_osc)

    def start(self):
        """Start MQTT client and OSC listener."""
        log.info("Connecting to MQTT broker %s:%s ...",
            self.mqtt_host, self.mqtt_port)
        self.mqttclient.connect(self.mqtt_host, self.mqtt_port)

        log.debug("Starting MQTT thread...")
        self.mqttclient.loop_start()

        log.info("Starting OSC server listening on port %s ...", self.osc_port)
        self.oscserver.start()

    def stop(self):
        """Method docstring."""
        log.info("Stopping OSC server ...")
        self.oscserver.stop()
        log.debug("Stopping MQTT thread ...")
        self.mqttclient.loop_stop()
        log.info("Disconnecting from MQTT broker ...")
        self.mqttclient.disconnect()

    def mqtt_connect(self, client, userdata, flags, rc):
        log.debug("MQTT connect: %s", mqtt.connack_string(rc))
        if rc == 0:
            client.subscribe(self.subscriptions)

    def mqtt_disconnect(self, client, userdata, rc):
        log.debug("MQTT disconnect: %s", mqtt.error_string(rc))

    def handle_mqtt(self, client, userdata, msg):
        log.debug("MQTT recv: %s %r", msg.topic, msg.payload)
        res = self.converter.from_mqtt(msg.topic, msg.payload)
        if res:
            if self.osc_receiver:
                log.debug("OSC send: %s %r", *res)
                self.oscserver.send(self.osc_receiver, res[0], *res[1])
        else:
            log.debug("No rule match for MQTT topic '%s'.", msg.topic)

    def handle_osc(self, oscaddr, values, tags, clientaddr, userdata):
        log.debug("OSC recv: %s %r", oscaddr, values)
        res = self.converter.from_osc(oscaddr, values, tags)
        if res:
            log.debug("MQTT publish: %s %r", *res)
            self.mqttclient.publish(*res)
        else:
            log.debug("No rule match for OSC address '%s'.", oscaddr)


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        '-c', '--config',
        metavar='FILENAME',
        default='osc2mqtt.ini',
        help="Read configuration from given filename")
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
        '-v', '--verbose',
        action="store_true",
        help='Enable verbose logging')

    args = ap.parse_args(args if args is not None else sys.argv[1:])

    cfg = read_config(args.config)

    for opt in ('mqtt_broker', 'osc_port', 'osc_receiver', 'verbose'):
        argval = getattr(args, opt)
        if opt not in cfg or argval != ap.get_default(opt):
            cfg[opt] = argval

    logging.basicConfig(level=logging.DEBUG
        if as_bool(cfg["verbose"]) else logging.INFO,
        format="%(levelname)s:%(message)s")

    converter = Osc2MqttConverter(cfg["rules"])
    osc2mqtt = Osc2MqttBridge(cfg, converter)
    osc2mqtt.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Interrupted.")
    finally:
        osc2mqtt.stop()
        log.info("Done.")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
