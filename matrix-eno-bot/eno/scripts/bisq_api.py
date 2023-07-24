#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import requests
import sqlite3
from datetime import date
from datetime import timedelta
#import random



def send_message(msg:str, room:str):
	com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -m "' + msg + '"' +" --room '" + room + "'"
	
	try:
		ret = subprocess.check_output(com, shell=True)
	except subprocess.CalledProcessError as e:
		print("Error launching matrix-commander")

def api_call(url: str):
	com = 'curl -sSL "' + url + '"'
	try:
		retval = subprocess.check_output(com, shell=True)
	except subprocess.CalledProcessError as e:
		print("Error making api call")

	return(retval)

def parse_kraken(data: dict):
	out = ''
	out = out + 'ask price:' + data['a'][0] + ', whole lot volume:' +data['a'][1] + ', lot volume:' + data['a'][2] + '\n'
	out = out + 'bid price:' +data['b'][0] + ', whole lot volume:' + data['b'][1] + ', lot volume:' + data['b'][2] + '\n'
	out = out + 'last trade closed price:' + data['c'][0] + ', lot volume:' + data['c'][1] + '\n'
	out = out + 'volume today:' + data['v'][0] + ', last 24-hours:' + data['v'][1] + '\n'
	out = out + 'volume weighted average price today:' + data['p'][0] + ', last 24-hours:' + data['p'][1] + '\n'
	out = out + 'number of trades today:' + str(data['t'][0]) + ', last 24-hours:' + str(data['t'][1]) + '\n'
	out = out + 'low price today:' + data['l'][0] + ', last 24-hours:' + data['l'][1] + '\n'
	out = out + 'high price today:' + data['h'][0] + ', last 24-hours:' + data['h'][1] + '\n'
	out = out + 'todays opening price:' + data['o'] + '\n'
	return out


if __name__ == "__main__":
    line = " ".join(sys.argv[1:])
#    print(line)
#    exit(0)
#    mbdx = line.find('=')
    market = line
    url = 'https://bisq.markets/api/ticker?market=' + market
    ret = api_call(url)
#    print(ret)
#    exit(0)
    buffer = json.loads(ret)
#    print(buffer)
#    print("bisq Market: " + market)
    return_string = "bisq Market: " + market
    return_string = return_string + "\n======================\n"
#    print("======================")
    try:
        for x in buffer:
#            print(x)
 #       print(x + ":" + str(buffer[x]))
            return_string = return_string + x + ":" + str(buffer[x] + '\n')
    except:
        y =1
#    exit(0)
    if market == 'XMR_BTC':
        url = 'https://api.kraken.com/0/public/Ticker?pair=XMRBTC'
        ret = api_call(url)
        buffer = json.loads(ret)
        data = buffer['result']['XXMRXXBT']
        kraken = parse_kraken(data)

        return_string = return_string + '\n' + 'Kraken Market:' + market + "\n======================\n" + kraken + '\n'
    print(return_string)
