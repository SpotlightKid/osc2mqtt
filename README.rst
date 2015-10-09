osc2mqtt
########

An OSC_ to MQTT_ bridge based on pyliblo_ and `paho-mqtt`_.

Quick Start
-----------

1. `pip install osc2mqtt`
2. Get osc2mqtt.ini_ and edit the `options` section and set your MQTT broker
   host and port and, optionally, an OSC host and port as a reveiver.
3. Run `osc2mqtt -v` and start publishing MQTT messages or sending OSC
   messages to `udp://localhost:9001/`.
4. Watch debugging output for the MQTT topics, OSC addresses and the kind of
   MQTT message payload and OSC arguments the messages have.
5. Add conversion rules to `osc2mqtt.ini` as needed. The `DEFAULT` section has
   helpful comments. Also change the `subscriptions` option to only receive the
   MQTT messages you're interested in.
6. Quit `osc2mqtt` with Control-C and restart it to try out your new
   configuration. Repeat from step 4, if necessary.

.. _osc: http://opensoundcontrol.org/
.. _mqtt: http://mqtt.org/
.. _paho-mqtt: https://www.eclipse.org/paho/clients/python/
.. _pyliblo: http://das.nasophon.de/pyliblo/
.. _osc2mqtt.ini: https://github.com/SpotlightKid/osc2mqtt/blob/master/osc2mqtt.ini
