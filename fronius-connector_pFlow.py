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
        url = "http://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi".format(FRONIUS_HOST)
        r = requests.get(url, timeout=FREQUENCY - 0.5)
        r.raise_for_status()
        powerflow_data = r.json()
        values['p_pv'] = powerflow_data['Body']['Data']['Site']['P_PV']
        values['p_grid'] = powerflow_data['Body']['Data']['Site']['P_Grid']
        values['p_load'] = -powerflow_data['Body']['Data']['Site']['P_Load']
        values['e_day'] = powerflow_data['Body']['Data']['Inverters']['1']['E_Day'] / 1000
        values['e_year'] = powerflow_data['Body']['Data']['Inverters']['1']['E_Year'] / 1000
        values['e_total'] = powerflow_data['Body']['Data']['Inverters']['1']['E_Total'] / 1000
        values['timestamp'] = powerflow_data['Head']['Timestamp']

        # handling for null/None values
        for k, v in values.items():
            if v is None:
                values[k] = 0

        time = datetime.datetime.utcnow()
        input_points = json.dumps(
		{
		  'measurement': 'FroniusPFlow',
		  'time': values['timestamp'],
		  'fields': {
		    'p_pv': float(values['p_pv']),
		    'p_grid': float(values['p_grid']),
		    'p_load': float(values['p_load']),
		    'e_day': values['e_day'],
		    'e_year': values['e_year'],
		    'e_total': values['e_total'],
		  }
		})
    except requests.exceptions.Timeout:
        print("Timeout requesting {}".format(url))
        return "TimeOut"
    except requests.exceptions.RequestException as e:
        print("requests exception {}".format(e))

    print(input_points)
    return input_points


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('fronius-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(FRONIUS_MQTT_PREFIX), "Fronius Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(FRONIUS_MQTT_PREFIX), "Fronius Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            X = fronius_data()
            if X !='TimeOut':     # Dont publish if timeout - may chrash the influxdb-connector.
              body = '['+X+']'
              (result, mid) = mqttc.publish(FRONIUS_MQTT_PREFIX+'/PFlow', body, 0)
              logging.debug("Publish Result: {} MID: {}".format(result, mid))               
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(FRONIUS_MQTT_PREFIX), "Fronius Connector: OFF-LINE", retain=True)
    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
