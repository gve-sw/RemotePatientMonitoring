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


import requests, yaml, json
from flask import Flask, request, redirect, url_for, render_template
from csv import DictReader


cred = yaml.safe_load(open("credentials.yml"))
WT_ADMIN_TOKEN = cred['WT_ADMIN_TOKEN']
MERAKI_KEY = cred['MERAKI_KEY']
MERAKI_NETWORK_ID = cred['MERAKI_NETWORK_ID']


# Room Data, from csv file
MerakiCamera_to_WebexRoomKitMini = []
with open('MerakiCameras_to_WebexRoomKitMini_Pairing.csv', 'r') as read_obj:
    csv_dict_reader = DictReader(read_obj)
    for row in csv_dict_reader:
        row['Room_Name'] = row.pop('ï»¿Room_Name')
        MerakiCamera_to_WebexRoomKitMini.append(row)
# note the use case is developed with only one patient room available, requires iterations if multiple rooms are listed in MerakiCameras_to_WebexRoomKitMini_Pairing.csv
MERAKI_SN = MerakiCamera_to_WebexRoomKitMini[0]['Meraki_SN']
ROOM_NAME = MerakiCamera_to_WebexRoomKitMini[0]['Room_Name']
ROOMKIT_ID = MerakiCamera_to_WebexRoomKitMini[0]['Webex_RoomKitMini_ID']
SIP_URL = MerakiCamera_to_WebexRoomKitMini[0]['Webex_RoomKitMini_SIP']


app = Flask(__name__)


@app.route('/')
def pop_up():
    snapshot_url = "https://api.meraki.com/api/v0/networks/{1}/cameras/{0}/snapshot".format(MERAKI_SN, MERAKI_NETWORK_ID)

    headers = {
        'X-Cisco-Meraki-API-Key': MERAKI_KEY,
        "Content-Type": "application/json"
    }
    resp = requests.post(snapshot_url, headers=headers, json={})
    r = json.loads(resp.text)

    snapshot = str(r["url"])
    snapshot_url = snapshot.replace(" ", "")

    return render_template('popup.html', room=ROOM_NAME, sip_url=SIP_URL, token=WT_ADMIN_TOKEN, snapshot_url=snapshot_url)


if __name__ == "__main__":
    app.run()