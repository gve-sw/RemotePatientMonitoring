'''
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''


import json, time, yaml, webbrowser
import paho.mqtt.client as mqtt
from csv import DictReader


cred = yaml.safe_load(open("credentials.yml"))


# Room Data, from csv file
MerakiCamera_to_WebexRoomKitMini = []
with open('MerakiCameras_to_WebexRoomKitMini_Pairing.csv', 'r') as read_obj:
    csv_dict_reader = DictReader(read_obj)
    for row in csv_dict_reader:
        row['Room_Name'] = row.pop('Room_Name')
        MerakiCamera_to_WebexRoomKitMini.append(row)
# note the use case is developed with only one patient room available, requires iterations if multiple rooms are listed in MerakiCameras_to_WebexRoomKitMini_Pairing.csv
ROOM_NAME = MerakiCamera_to_WebexRoomKitMini[0]['Room_Name']
MERAKI_SN = MerakiCamera_to_WebexRoomKitMini[0]['Meraki_SN']
MERAKI_ZONE_ID = MerakiCamera_to_WebexRoomKitMini[0]['Meraki_Zone_ID']



# MQTT
MQTT_SERVER = cred['MQTT_SERVER']
MQTT_PORT = cred['MQTT_PORT']
MQTT_TOPIC = "/merakimv/" + MERAKI_SN + "/" + MERAKI_ZONE_ID



# motion trigger setting
MOTION_ALERT_PEOPLE_COUNT_THRESHOLD = 1
MOTION_ALERT_ITERATE_COUNT = 20
MOTION_ALERT_TRIGGER_PEOPLE_COUNT = 1
MOTION_ALERT_PAUSE_TIME = 30
_MONITORING_TRIGGERED = False
_MONITORING_MESSAGE_COUNT = 0
_MONITORING_PEOPLE_TOTAL_COUNT = 0



def collect_information(topic, payload):

    # detect motion
    global _MONITORING_TRIGGERED, _MONITORING_MESSAGE_COUNT, _MONITORING_PEOPLE_TOTAL_COUNT

    # if motion monitoring triggered
    if _MONITORING_TRIGGERED:

        _MONITORING_MESSAGE_COUNT = _MONITORING_MESSAGE_COUNT + 1

        _MONITORING_PEOPLE_TOTAL_COUNT = _MONITORING_PEOPLE_TOTAL_COUNT + payload

        if _MONITORING_MESSAGE_COUNT > MOTION_ALERT_ITERATE_COUNT:

            if _MONITORING_PEOPLE_TOTAL_COUNT >= MOTION_ALERT_TRIGGER_PEOPLE_COUNT:

                # alert
                alert()
                # pause
                time.sleep(MOTION_ALERT_PAUSE_TIME)

            # reset
            _MONITORING_MESSAGE_COUNT = 0

            _MONITORING_PEOPLE_TOTAL_COUNT = 0

            _MONITORING_TRIGGERED = False

    if payload >= MOTION_ALERT_PEOPLE_COUNT_THRESHOLD:
        _MONITORING_TRIGGERED = True


def alert():
    # open URL
    webbrowser.open_new('http://127.0.0.1:5000/')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode("utf-8"))
    payload = payload["counts"]["person"]
    collect_information(msg.topic, payload)


if __name__ == "__main__":
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_SERVER, MQTT_PORT, 60)
        client.loop_forever()

    except Exception as ex:
        print("[MQTT] failed to connect or receive msg from mqtt, due to: \n {0}".format(ex))
