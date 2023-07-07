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

def verify_signature(challenge: str, id: str, signature: str):

	url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
	headers = {'content-type': 'application/json'}
# Now let's sign the challenge...
	rpc_input2 = {
		"method": "verify",
		"params": {"data": challenge,
		"address":id,
		"signature":signature}
	}
	rpc_input2.update({"jsonrpc": "2.0", "id": "0"})
	response2 = requests.post(url,data=json.dumps(rpc_input2),headers=headers)
	sd = response2.json()
	retval = sd["result"]["good"]
#	print(retval)
	if retval:
		return True
	else:
		return False

def process_verify_signature(line: str,srch_pattern: str,room: str, id_number: int):
# check if "verify_signature" present on a current line
    print(line)
    report_room = room
    idx = line.find(srch_pattern)
    print(idx)
    if idx != -1:
        print("Found search pattern...")
        print(line)
        rdx = line.find(room) # room_addr?
        if rdx == -1:
            print(srch_pattern + "NOT in " + room + "!")
            rdx = line.find(anon_room_addr)
            if rdx == -1:
                return False
            else:
                report_room = anon_room_addr
        print("In correct room, Killing matrix-commander process...")
        retval = kill_commander()
# Make sure there is a data_string...
        idx = line.find("data")
        if idx == -1:
            print("No data string, exiting.")
            exit(1) 
        print(srch_pattern, 'string exists in file')
        jbx = line.find('{"json')
        jex = line.find("}}")
        print("Start:" + str(jbx))
        print("End:" + str(jex))
        js = line[jbx:jex+2]
#js is the json string...
        buffer = json.loads(js)
        print("json string:")
        print(buffer)
        print("Message line: " + line)

#int/str issue
        data = str(buffer['params']['data'])
        signature = buffer['params']['signature']
        print("Data String:")
        print(data)
        if report_room == room_addr:
            address = get_id(room_id)
            si = room_id
        if report_room == anon_room_addr:
            address = get_id(anon_room_id)
            si = anon_room_id
        print("Data: " + data)
        print("ID: " + address)
        val = verify_signature(data, address, signature)
        if val:
            retval = "valid signature"
        else:
            retval = "bad signature"
        js = js = '{"json":"2.0","method":"signature_result","params":{"result":"' + retval + '"'
# Populate signature verification URL with the parameters...
        for x in buffer['params']:
            js = js + ',"' + x + '":"' + buffer['params'][x] + '"'
        js = js + '}}'
        com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + "store -m '" + js + "'" +" --room '" + report_room + "'"
        print(com)
        try:
            ret = subprocess.check_output(com, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error launching matrix-commander")
            print(e.output)
            return False
        return True


def sign(challenge: str, id: str, id_index: int):

    url = "http://127.0.0.1:18089/json_rpc"
    headers = {'content-type': 'application/json'}
# Now let's sign the challenge...
    rpc_input2 = {
        "method": "sign",
        "params": {"data": challenge,
            "account_index":id_index,
            "signature_type":"spend"}
        }
    rpc_input2.update({"jsonrpc": "2.0", "id": "0"})
    response2 = requests.post(url,data=json.dumps(rpc_input2),headers=headers)
    sd = response2.json()
    signature = sd["result"]["signature"]
#    print("Signature: " + signature)
    return signature

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
    line = " ".join(sys.argv[1:])
#    print(line)
#    exit(0)
#    print(line)
#    exit(0)
    jbx = line.find('{"json')
    jex = line.find("}}}",jbx)
    if jex == -1:
        jex = line.find("}}",jbx)
        js = line[jbx:jex+2]
    else:
        js = line[jbx:jex+3]
    #print(line)
# Put the commas back!
    x = js.replace('" "', '","')
    js = x
    #print("js: " + js)
    buffer = json.loads(js)
#    print(buffer)
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

    data = str(buffer['params']['data'])
    try:
        id_index = buffer['params']['id_index']
    except:
        id_index = 0 # Default if no id_index provided
    address = buffer['params']['id']
    signature = buffer['params']['signature']

    val = verify_signature(data, address, signature)
    if val:
        retval = "valid signature"
    else:
        retval = "bad signature"

    print(retval)
