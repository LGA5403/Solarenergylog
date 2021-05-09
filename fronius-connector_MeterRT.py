#!/usr/bin/env python

"""Fetches some data from the fronius json api
and publishes the result to mqtt.
Read only."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import datetime
import time
import logging
import sys
import json
from config import *


FREQUENCY = 3


def fronius_data():

    input_points = {}
    values = {}
    try:
        url = "http://{}/solar_api/v1/GetMeterRealtimeData.cgi?Scope=Device&DeviceId=0".format(FRONIUS_HOST)
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        powerflow_data = r.json()
#        print(powerflow_data)
        values['WAC_Produced'] = powerflow_data['Body']['Data']['EnergyReal_WAC_Sum_Produced']
        values['WAC_Consumed'] = powerflow_data['Body']['Data']['EnergyReal_WAC_Sum_Consumed']
        values['timestamp'] = powerflow_data['Head']['Timestamp']

        # handling for null/None values
        for k, v in values.items():
            if v is None:
                values[k] = 0
#        'TS': values['timestamp']

        time = datetime.datetime.utcnow()
        input_points = json.dumps(
		{
		  'measurement': 'FroniusMeterRT',
		  'time': values['timestamp'],
		  'fields': {
		    'WAC_Produced': float(values['WAC_Produced']),
		    'WAC_Consumed': float(values['WAC_Consumed']),
		  }
		})

    except requests.exceptions.Timeout:
        print("Timeout requesting {}".format(url))
        return "TimeOut"
    except requests.exceptions.RequestException as e:
        print("requests exception {}".format(e))

    return input_points


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('fronius-connector_MeterRT', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(FRONIUS_MQTT_PREFIX), "Fronius Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(FRONIUS_MQTT_PREFIX), "Fronius Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            X = fronius_data()
            if X !='TimeOut': 
              body = '['+X+']'
              print (body)
              (result, mid) = mqttc.publish(FRONIUS_MQTT_PREFIX+'/Fld1', body, 0)
            time.sleep(10)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(FRONIUS_MQTT_PREFIX), "Fronius Connector: OFF-LINE", retain=True)
    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
