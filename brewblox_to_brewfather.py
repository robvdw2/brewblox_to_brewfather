#!/usr/bin/python3
import yaml
import json
import requests
import urllib3
import time
import datetime
import sys
import os

# Search key of fields based on value
def fieldSearch(value):
    for k,v in fields.items():
        if v == value:
            return k
    return False

# Don't submit Null/None data
def removeNone(d):
    out = {}
    for k,v in d.items():
        if(v != 'None'):
            out[k] = v
    return out

# Load and process config file
try:
    yamlfile = open(os.path.join(sys.path[0], "brewblox_to_brewfather.yml"))
    conf = yaml.safe_load(yamlfile)
except:
    print("Error loading confiration file brewblox_to_brewfather.yml: ",sys.exc_info()[0])
    sys.exit()

bfdata = conf['brewfatherdata']
headers = { 'Content-Type': 'application/json' }
urllib3.disable_warnings()

# List of fields accross devices
fields = {}
for device in conf['brewblox']['devices']:
    for measurement, devicefields in device.items():
        for f,v in devicefields.items():
            fields[f] = v

while True:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Query Brewblox for each device
    for device in conf['brewblox']['devices']:
        for measurement,devicefields in device.items():
            brewblox_params = { 'measurement': measurement, 'fields': list(devicefields.values()) }
            response = requests.post(conf['brewblox']['url'], json=brewblox_params, headers=headers, verify=False)
            if response.status_code == 200:
                for r in response.json():
                    field = fieldSearch(r['field'])
                    if field:
                        bfdata[field] = r['value']
                    else:
                        print(timestamp+" Field "+r['field']+" not recognized")

    # Write to brewfather
    brewfather_params = removeNone(bfdata)
    bf_response = requests.post(conf['brewfather']['url'], json=brewfather_params, headers=headers, verify=False)
    if bf_response.status_code == 200:
        result = bf_response.json()['result']
        if result == "success":
            print(timestamp+" Data submitted succesfully")
        elif result == "ignored":
            print(timestamp+" Data submission ignored (leave 900 seconds between logging)")
        else:
            print(timestamp+" "+bf_response.text)
    else:
        print(timestamp+" Request to Brewfather API failed with HTTP error code "+bf_response.status_code)

    if conf['brewfather']['interval'] != 0:
        time.sleep(conf['brewfather']['interval'])
    else:
        sys.exit()
