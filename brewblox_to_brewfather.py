#!/usr/bin/python3
import datetime
import os
import sys
import time

import requests
import urllib3
import yaml

urllib3.disable_warnings()

# Load and process config file
try:
    yamlfile = open(os.path.join(sys.path[0], 'brewblox_to_brewfather.yml'))
    conf = yaml.safe_load(yamlfile)
except Exception:
    print('Error loading confiration file brewblox_to_brewfather.yml: ',
          sys.exc_info()[0])
    sys.exit()

bfdata = conf['brewfatherdata']
brewblox_url = conf['brewblox']['url']
metrics_url = f'{brewblox_url}/history/timeseries/metrics'
brewblox_params = {'fields': list(conf['brewblox']['fields'].values())}

# Key is brewblox field, value is brewfather field
reverse_fields = {
    v: k
    for k, v in conf['brewblox']['fields'].items()
}

while True:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Query Brewblox fields
    response = requests.post(metrics_url, json=brewblox_params, verify=False)

    if response.status_code == 200:
        for response_value in response.json():
            brewblox_field = response_value['metric']
            brewfather_field = reverse_fields.get(brewblox_field)
            if brewfather_field in bfdata:
                bfdata[brewfather_field] = response_value['value']
            else:
                print(f'{timestamp} Field {brewfather_field} not recognized')

    else:
        print(f'{timestamp} Request to Brewblox API failed' +
              f' with HTTP error {response.status_code} {response.text}')

    # Write to brewfather
    brewfather_params = {
        k: v
        for k, v in bfdata.items()
        if v is not None
    }

    bf_response = requests.post(conf['brewfather']['url'],
                                json=brewfather_params,
                                verify=False)
    if bf_response.status_code == 200:
        result = bf_response.json()['result']
        if result == 'success':
            print(f'{timestamp} Data submitted succesfully')
        elif result == 'ignored':
            print(f'{timestamp} Data submission ignored' +
                  ' (leave 900 seconds between logging)')
        else:
            print(f'{timestamp} {bf_response.text}')
    else:
        print(f'{timestamp} Request to Brewfather API failed' +
              f' with HTTP error code {bf_response.status_code}')

    if conf['brewfather']['interval'] != 0:
        time.sleep(conf['brewfather']['interval'])
    else:
        sys.exit()
