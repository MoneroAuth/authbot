#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import requests
import sqlite3
import secrets
from qrcodegen import QrCode, QrSegment
from datetime import date
from datetime import timedelta
#import random


def get_id(address_index):

#   print("About to get the Monero address")
    url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {
        "method": "get_address",
        "params": {"account_index":0, "address_index":[address_index]
              }
    }

    rpc_input.update({"jsonrpc": "2.0", "id": "0"})
#    print(json.dumps(rpc_input))
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    jd = response.json()
#   print(jd['result']['subaddress_accounts'][0]['base_address'])
    try:
        id = jd['result']['addresses'][0]['address']
    except:
        id = None
#    account_index = jd['result']['subaddress_accounts'][0]['account_index']
#    address_info = [id, account_index]
    return id


if __name__ == "__main__":
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

    sender = os.environ.get('ENO_SENDER')
    if sender != authbot_owner:
        print(sender + " your not authorized!")
        exit(0)

    line = " ".join(sys.argv[1:])
#    print(line)
#    exit(0)
    if len(line) == 0:
        print("You must supply an ID index number!")
        exit(0)
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

    id_index = int(line)
#    print(line)
    address = get_id(id_index)
    if address is None:
        print("Invalid ID index!")
        exit(0)
#    anon_addr = get_id(1)
    print("Address: " + address)
#    print("Anon address: " + anon_addr)
