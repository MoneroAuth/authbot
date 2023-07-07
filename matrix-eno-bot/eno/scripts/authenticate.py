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
from cairosvg import svg2png

def to_svg_str(qr: QrCode, border: int) -> str:
        """Returns a string of SVG code for an image depicting the given QR Code, with the given number
        of border modules. The string always uses Unix newlines (\n), regardless of the platform."""
        if border < 0:
                raise ValueError("Border must be non-negative")
        parts: List[str] = []
        for y in range(qr.get_size()):
                for x in range(qr.get_size()):
                        if qr.get_module(x, y):
                                parts.append(f"M{x+border},{y+border}h1v1h-1z")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {qr.get_size()+border*2} {qr.get_size()+border*2}" stroke="none">
        <rect width="100%" height="100%" fill="#FFFFFF"/>
        <path d="{" ".join(parts)}" fill="#000000"/>
</svg>
"""

def print_qr(qrcode: QrCode) -> None:
        """Prints the given QrCode object to the console."""
        border = 4
        for y in range(-border, qrcode.get_size() + border):
                for x in range(-border, qrcode.get_size() + border):
                        print("\u2588 "[1 if qrcode.get_module(x,y) else 0] * 2, end="")
                print()
        print()


def purge_challenge(purge_date: str):
	try:
		dbconnect = sqlite3.connect(authbot_path + "authbot")
		cursor = dbconnect.cursor()
		sql = "DELETE FROM challenge WHERE issued < '" + purge_date + "'"
#		print(sql)
		count = cursor.execute(sql)
		dbconnect.commit()
		cursor.close()
		return True
	except sqlite3.Error as error:
		print("Failed to remove records.", error)
	finally:
		if dbconnect:
			dbconnect.close()
			print("Database connection closed.")
			return False

def db_challenge(cs: str):
	try:
		dbconnect = sqlite3.connect(authbot_path + "authbot")
		dbconnect.row_factory = sqlite3.Row
		cursor = dbconnect.cursor()
		sql = "SELECT challenge_string, issued FROM challenge WHERE challenge_string = '" + cs + "'"
#		print(sql)
		cursor.execute(sql)
		rs = cursor.fetchone()
		if rs == None:
			print('Empty result set!')
			dbconnect.close()
			return False
		if rs['challenge_string'] == cs:
#			print(rs['challenge_string'], rs['issued'])
			print("Reuse Detected. Ignoring!")
			dbconnect.close()
			return True
		dbconnect.close()
		return False
	except sqlite3.Error as error:
		print("Failed to query database.", error)

def store_challenge(challenge_string: str):
	try:
		dbconnect = sqlite3.connect(authbot_path + "authbot")
		cursor = dbconnect.cursor()
		sql = "INSERT INTO challenge(challenge_string) VALUES('" + challenge_string + "')"
#		print(sql)
		count = cursor.execute(sql)
		dbconnect.commit()
		cursor.close()
		return True
	except sqlite3.Error as error:
		print("Failed to insert record into the database.", error)
		return False
#	finally:
#		if dbconnect:
#			dbconnect.close()
#			print("Database connection closed.")
#			return False

def get_id(address_index):

#   print("About to get the Monero address")
    url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {
        "method": "get_address",
        "params": {"account_index":address_index, "address_index":[0]
              }
    }

    rpc_input.update({"jsonrpc": "2.0", "id": "0"})
#    print(json.dumps(rpc_input))
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    jd = response.json()
#   print(jd['result']['subaddress_accounts'][0]['base_address'])
    id = jd['result']['addresses'][0]['address']
#    account_index = jd['result']['subaddress_accounts'][0]['account_index']
#    address_info = [id, account_index]
    return id

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

def generate_json(d,challenge_msg):
	if 'dataset' not in d.keys():
		for x in d['params']:
			#print(x)
			challenge_msg = challenge_msg + ',"' + x + '":"' + str(d['params'][x]) + '"'
		challenge_msg = challenge_msg + '}}'
	else:
		for x in d['params']:
			#print(x)
			if x == 'dataset':
				challenge_msg = challenge_msg + ',"' + x + '":'
				ds = str(d['params']['dataset'])
				dsm = ds.replace("'", '"')
				challenge_msg = challenge_msg + dsm + "}}"
				break
			else:
				challenge_msg = challenge_msg + ',"' + x + '":"' + str(d['params'][x]) + '"'
					
	return challenge_msg


if __name__ == "__main__":
    line = " ".join(sys.argv[1:])
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
    x = js.replace(" ", ",")
    js = x
    #print("js: " + js)
    buffer = json.loads(js)
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

#    print(monero_wallet_rpc_port)
#    print(os.environ.get('ENO_ROOM'))
    room = os.environ.get('ENO_ROOM')
 #   exit(0)
#    print("TESTING:")
#    print(buffer)
#    print("json string:")
#    print(buffer)
    
    cs = buffer['params']['challenge_string']
    ce = db_challenge(cs)
    if ce: # If challenge_string is already in the db, then stop processing this message!
#        print(ce)
        print("challenge_string: " + cs + " has already been used!")
        exit(0)
    if ce == 'DBError!':
        print("Database error!")
        exit(1)
    sigVerificationURL = buffer['params']['signature_verification']
#        sigVerificationURL =  buffer['params']['signature_verification'] + "?challenge=" + buffer['params']['challenge_string']
#strip a trailing "/" if it exists...
    q = len(sigVerificationURL)
    sigVerificationURL = sigVerificationURL[0:q]
    sigVerificationURL = sigVerificationURL + "?challenge=" + buffer['params']['challenge_string']
#    print(js)
    challenge = buffer['params']['challenge_string']
#int/str issue
    challenge = str(buffer['params']['challenge_string'])
#    print("Challenge String:")
#    print(challenge)
#    address = get_id(0)
#    print("Challenge: " + challenge)
#    print("Address: " + address)
    try:
        id_index =int( buffer['params']['id_index'])
    except:
        id_index = 0 # Default ID is public facing...
    address = get_id(id_index)
    signature = sign(challenge, address, id_index)
# Populate signature verification URL with the parameters...
    for x in buffer['params']:
        if x != 'signature_verification' and x != 'challenge_string' and x != 'id_index':
            sigVerificationURL = sigVerificationURL + "&" + x + "=" + buffer['params'][x]
    sigVerificationURL = sigVerificationURL + "&id=" + address + "&signature=" + signature
#    print("Signature Verification URL: " + sigVerificationURL)
    text = '{"json":"2.0","method":"digital_signature","params":{"?challenge":"' + challenge + '","address":"' + address + '"signature":"' + signature + '"}}'
#    print(text)
        #errcorlvl = QrCode.Ecc.HIGH  # Error correction level
        # To obtain larger QR Code in the element message window...
    errcorlvl = QrCode.Ecc.LOW  # Error correction level

        # Make and print the QR Code symbol
#            qr = QrCode.encode_text(text, errcorlvl)
#Make QR code of Signature Verification URL...
#    print(sigVerificationURL)
    qr = QrCode.encode_text(sigVerificationURL, errcorlvl)
    print_qr(qr)
    print(to_svg_str(qr,4))
    sv = to_svg_str(qr,4)
#    print("writing QR code to " + authbot_path + "output.png")
    svg2png(bytestring=sv,write_to=authbot_path + 'output.png')
#    print(sigVerificationURL)
# DEBUG...
    if room is None:
        room = '!HbBCqWmZWeCTSmjkJh:authbot.org'
#    print(room)
#    print(matrix_commander_path)
#    print(authbot_path)
#    print(cs)
    com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -i ' + authbot_path + 'output.png -m "' + sigVerificationURL + '"' +" --room '" + room + "'"
    retval = store_challenge(cs)
#    print(retval)
    if not retval:
        exit(1)
 #   print(com)
    try:
        ret = subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error launching matrix-commander")
        print(e.output)
        exit(1)
    yesterday = date.today() - timedelta(days=1)
    retval = purge_challenge(str(yesterday))
