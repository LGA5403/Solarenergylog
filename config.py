#!/usr/bin/env python

BROKER_HOST = '192.168.1.73'
BROKER_PORT = 1883

INFLUXDB_HOST = '192.168.1.73'
FRONIUS_HOST = '192.168.1.70'
FRONIUS_MQTT_PREFIX = 'fronius'

MODBUS_HOST1 = 'fronius.kleber'
BATTERY_MQTT_PREFIX1 = 'battery'

PV_P_TOPIC1 = 'fronius/p_pv'
SET_CHG_PCT_TOPIC1 = 'battery/set/chg_pct'
CHG_PCT_TOPIC1 = 'battery/chg_pct'
AUTO_CHG_TOPIC1 = 'battery/auto_chg_pct'
SOC_TOPIC1 = 'fronius/soc'

GOECHARGER_HOST1 = 'go-echarger.kleber'
GOECHARGER_MQTT_PREFIX = 'goe'

NETATMO_MQTT_PREFIX1 = 'netatmo'

ZOE_MQTT_PREFIX1 = 'zoe'

HEATER_MQTT_PREFIX1 = 'heater'

VCONTROLD_MQTT_PREFIX1 = 'vcontrold'
