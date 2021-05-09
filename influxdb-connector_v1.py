#!/usr/bin/env python3
# https://thingsmatic.com/2017/03/02/influxdb-and-grafana-for-sensor-time-series/
import paho.mqtt.client as mqtt
import datetime
import time
import json
from influxdb import InfluxDBClient
from config import *


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("fronius/#")


def on_message(client, userdata, msg):
    print("Received a message on topic: " + msg.topic)
    # Use utc as timestamp
    receiveTime = datetime.datetime.utcnow()

    m_decode=str(msg.payload.decode("utf-8","ignore"))
#    print ("\ndata m_decode-type ",type(m_decode))
    if m_decode != 'TimeOut':   # To avoid the connector to chrash on timeouts on the publisher
      if m_decode[0]=='[':
        message = json.loads(m_decode)
#        print("Message: ",message)
        dbclient.write_points(message)
#        print("Finished writing to InfluxDB")
      else:
        print ("No DATA!!!!!!!!!!!!!!!")   # This seems to happen on start.
    else:
      print('>>>>>>>>  TIMEOUT!!!!!  <<<<<<<<<<<')
print("start")

# Set up a client for InfluxDB
dbclient = InfluxDBClient(INFLUXDB_HOST, 8086, 'grafana', 'Mulan2010', 'fronius')
print("dbclient created")

# Initialize the MQTT client that should connect to the Mosquitto broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Wait for connect
connOK = False
while(connOK is False):
    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        connOK = True
    except Exception:
        connOK = False
    time.sleep(2)

print("mqtt connection established")

# Blocking loop to the Mosquitto broker
client.loop_forever()
