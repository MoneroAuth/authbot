####################################################################################################################################################
# AuthBot version 0.0.9
# Copyright (C) - 2023
# by Douglas Alan Bebber
# @dougbebber:matrix.org
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
####################################################################################################################################################
from datetime import date
from datetime import timedelta
import sys
import os
import json
import requests
from typing import List
from qrcodegen import QrCode, QrSegment
import random
from cairosvg import svg2png
import subprocess
import sqlite3

authbot_version = "0.0.9"

def purge_challenge(purge_date: str):
	try:
		dbconnect = sqlite3.connect(authbot_path + "authbot")
		cursor = dbconnect.cursor()
		sql = "DELETE FROM challenge WHERE issued > '" + purge_date + "'"
		print(sql)
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
		print(sql)
		cursor.execute(sql)
		rs = cursor.fetchone()
		if rs == None:
			print('Empty result set!')
			dbconnect.close()
			return False
		if rs['challenge_string'] == cs:
			print(rs['challenge_string'], rs['issued'])
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
		print(sql)
		count = cursor.execute(sql)
		dbconnect.commit()
		cursor.close()
		return True
	except sqlite3.Error as error:
		print("Failed to insert record into the database.", error)
	finally:
		if dbconnect:
			dbconnect.close()
			print("Database connection closed.")
			return False

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
    print(json.dumps(rpc_input))
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    jd = response.json()
#   print(jd['result']['subaddress_accounts'][0]['base_address'])
    id = jd['result']['addresses'][0]['address']
#    account_index = jd['result']['subaddress_accounts'][0]['account_index']
#    address_info = [id, account_index]
    return id

def next_index():

    url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {
        "method": "get_accounts",
        "params": {}
    }

    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    jd = response.json()
    accounts = jd['result']['subaddress_accounts']
    return len(accounts)

def create_id(tag: str):

    url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {
        "method": "create_account",
        "params": {"label":tag}
    }

    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    jd = response.json()
    id_info = [jd['result']['address'],jd['result']['account_index']]
#   id_info[0] = jd['result']['address']
#   id_info[1] = jd['result']['account_index']
    return id_info

def tag_id(tag: str, id_index: int):

    url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {
        "method": "tag_accounts",
        "params": {"tag":tag, "accounts":[id_index] }
    }

    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    jd = response.json()
    return True

def sign(challenge: str, id: str, id_index: int):

    url = "http://127.0.0.1:" + str(monero_wallet_rpc_port) + "/json_rpc"
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
    print("Signature: " + signature)
    return signature


def kill_commander():

    l = subprocess.check_output('ps aux | grep "matrix-commander"' , shell =True)
    res = l.split()
    print(res)
    print()
    print(res[1])

    port = int(res[1])
    print(port)
    com = "kill " + str(port)
    print(com)

    try:
        ret = subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        return False
    return True

def commander_up ():

	l = subprocess.check_output('ps aux | grep "matrix-commander"' , shell =True)
	res = l.split()
	print('res:')
	print(res)
	print()
	print(res[1])
	if b'--listen' in res:
		print('Commander is running')
		return True
	else:
		print('Commander is NOT running')
		com = matrix_commander_path + "matrix-commander --credentials " + authbot_path + "credentials.json --store " + authbot_path + "store --listen forever --listen-self --download-media " + download_media_path + " >" + message_capture_file + " &"
		print(com)
		try:
			ret = subprocess.check_output(com, shell=True)
		except subprocess.CalledProcessError as e:
			print(e.output)
			sleep(2)
		return True


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

def process_signature_verification(line: str,srch_pattern: str,room: str, id_number: int):
# check if string present on a current line
    print(line)
    report_room = room
    idx = line.find(srch_pattern)
    print(idx)
    if idx != -1:
        print("Found signature_verification...")
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
# Make sure there is a challenge_string...
        idx = line.find("challenge_string")
        if idx == -1:
            print("No challenge_string, exiting.")
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
        cs = buffer['params']['challenge_string']
        ce = db_challenge(cs)
        if ce: # If challenge_string is already in the db, then stop processing this message!
            print(ce)
            print("challenge_string: " + cs + " is already in the database!")
            return False
        if ce == 'DBError!':
            print("Database error!")
            return False
        print("Message line: " + line)
        sigVerificationURL = buffer['params']['signature_verification']
#        sigVerificationURL =  buffer['params']['signature_verification'] + "?challenge=" + buffer['params']['challenge_string']
#strip a trailing "/" if it exists...
        q = len(sigVerificationURL)
        sigVerificationURL = sigVerificationURL[0:q]
        sigVerificationURL = sigVerificationURL + "?challenge=" + buffer['params']['challenge_string']
        print(js)
        challenge = buffer['params']['challenge_string']
#int/str issue
        challenge = str(buffer['params']['challenge_string'])
        print("Challenge String:")
        print(challenge)
        if report_room == room_addr:
            address = get_id(room_id)
            si = room_id
        if report_room == anon_room_addr:
            address = get_id(anon_room_id)
            si = anon_room_id
        print("Challenge: " + challenge)
        print("Address: " + address)
        signature = sign(challenge, address, si)
# Populate signature verification URL with the parameters...
        for x in buffer['params']:
            if x != 'signature_verification' and x != 'challenge_string':
                sigVerificationURL = sigVerificationURL + "&" + x + "=" + buffer['params'][x]
        sigVerificationURL = sigVerificationURL + "&id=" + address + "&signature=" + signature
        print("Signature Verification URL: " + sigVerificationURL)
        text = '{"json":"2.0","method":"digital_signature","params":{"?challenge":"' + challenge + '","address":"' + address + '"signature":"' + signature + '"}}'
        print(text)
        #errcorlvl = QrCode.Ecc.HIGH  # Error correction level
        # To obtain larger QR Code in the element message window...
        errcorlvl = QrCode.Ecc.LOW  # Error correction level

        # Make and print the QR Code symbol
#            qr = QrCode.encode_text(text, errcorlvl)
#Make QR code of Signature Verification URL...
        print(sigVerificationURL)
        qr = QrCode.encode_text(sigVerificationURL, errcorlvl)
        print_qr(qr)
        print(to_svg_str(qr,4))
        sv = to_svg_str(qr,4)
        print("writing QR code to " + authbot_path + "output.png")
        svg2png(bytestring=sv,write_to=authbot_path + 'output.png')
        com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -i ' + authbot_path + 'output.png -m "' + sigVerificationURL + '"' +" --room '" + report_room + "'"
        retval = store_challenge(cs)
#        with open(authbot_path + 'last_message.txt', 'r') as fp:
#            last_message = fp.readlines()
#        fp.close()
#        if com == last_message:
#            return False # Already sent the message.
        print(com)
        try:
            ret = subprocess.check_output(com, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error launching matrix-commander")
            print(e.output)
            return False
#        with open(authbot_path + "last_message.txt","w") as f:
#            f.write(com)
#        f.close()
        yesterday = date.today() - timedelta(days=1)
        retval = purge_challenge(str(yesterday))
        return True

def process_version(line: str,srch_pattern: str,room: str, id_number: int):
# check if string present on a current line
    print(line)
    report_room = room
    idx = line.find(srch_pattern)
    print(idx)
    if idx != -1:
        print("Found " + srch_pattern)
        print(line)
        rdx = line.find(room_addr) # room_addr?
        if rdx == -1:
            print(srch_pattern + "NOT in " + room + "!")
            rdx = line.find(anon_room_addr)
            if rdx == -1:
                print(srch_pattern + "NOT in " + anon_room_addr + "!")
                return False
            else:
                report_room = anon_room_addr
        print("In correct room, Killing matrix-commander process...")
        retval = kill_commander()
        com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -m "authbot version: ' + authbot_version + '"' + " --room '" + report_room + "'"
        print(com)

        try:
            ret = subprocess.check_output(com, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error launching matrix-commander")
            print(e.output)
            return False
        return True

def process_id_lookup(line: str,srch_pattern: str,room: str, id_number: int):
# check if string present on a current line
    print(line)
    report_room = room
    idx = line.find(srch_pattern)
    print(idx)
    if idx != -1:
        print("Found " + srch_pattern)
        print(line)
        rdx = line.find(room_addr) # room_addr?
        if rdx == -1:
            print(srch_pattern + "NOT in " + room + "!")
            rdx = line.find(anon_room_addr)
            if rdx == -1:
                print(srch_pattern + "NOT in " + anon_room_addr + "!")
                return False
            else:
                report_room = anon_room_addr
        print("In correct room, Killing matrix-commander process...")
        retval = kill_commander()
        address = get_id(id_number)
        anon_addr = get_id(1)
        print("Address: " + address)
        print("Anon address: " + anon_addr)
        com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -m "Your public facing id is: ' + address + '\nYour anonymous id is: ' + anon_addr + '"' + " --room '" + report_room + "'"
        print(com)
#        com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -m "Your anonymous id is: ' + anon_addr + '"' +" --room '" + room + "'"
        try:
            ret = subprocess.check_output(com, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error launching matrix-commander")
            print(e.output)
            return False
        return True

def process_json_message(line: str,srch_pattern: str,room: str, id_number: int):
# check if string present on a current line
    print(line)
    report_room = room
    idx = line.find(srch_pattern)
    print(idx)
    if idx != -1:
        print("Found " + srch_pattern + "...")
        print(line)
        rdx = line.find(room_addr) # room_addr?
        if rdx == -1:
            print(srch_pattern + "NOT in " + room + "!")
            rdx = line.find(anon_room_addr)
            if rdx == -1:
                return False
            else:
                report_room = anon_room_addr
        print("In correct room, Killing matrix-commander process...")
        retval = kill_commander()
# Make sure there is a challenge_string...
        idx = line.find("challenge_string")
        if idx == -1:
            print("No challenge_string, exiting.")
            exit(1) 
# Now pull the sender username from the message...
        print("line: " + line)
        jbx = line.find('{"json')
        jex = line.find("}}")
        print("Start:" + str(jbx))
        print("End:" + str(jex))
        js = line[jbx:jex+2]
#js is the json string...
        buffer = json.loads(js)
        print("json string:")
        print(buffer)
        cs = buffer['params']['challenge_string']
        ce = db_challenge(cs)
        if ce: # If challenge_string is already in the db, then stop processing this message!
            print(ce)
            print("challenge_string: " + cs + " is already in the database!")
            return False
        if ce == 'DBError!':
            print("Database error!")
            return False
        print("Message line: " + line)
        challenge = buffer['params']['challenge_string']
#int/str issue
        challenge = str(buffer['params']['challenge_string'])
        print("Challenge String:")
        print(challenge)
        if report_room == room_addr:
            address = get_id(room_id)
            si = room_id
        if report_room == anon_room_addr:
            address = get_id(anon_room_id)
            si = anon_room_id
        print("Challenge: " + challenge)
        print("Address: " + address)
        signature = sign(challenge, address, si)
        js = '{"json":"2.0","method":"signature_verification","params":{"signature":"' + signature + '"'
        for x in buffer['params']:
            js = js + ',"' + x + '":"' + buffer['params'][x] + '"'
        js = js + '}}'
        print("json message: " + js)
#        text = '{"json":"2.0","method":"digital_signature","params":{"?challenge":"' + challenge + '","address":"' + address + '"signature":"' + signature + '"}}'
#        print(text)
        #errcorlvl = QrCode.Ecc.HIGH  # Error correction level
        # To obtain larger QR Code in the element message window...
        errcorlvl = QrCode.Ecc.LOW  # Error correction level

        # Make and print the QR Code symbol
#            qr = QrCode.encode_text(text, errcorlvl)
#Make QR code of Signature Verification URL...
        print(js)
        qr = QrCode.encode_text(js, errcorlvl)
        print_qr(qr)
        print(to_svg_str(qr,4))
        sv = to_svg_str(qr,4)
        print("writing QR code to " + authbot_path + "output.png")
        svg2png(bytestring=sv,write_to=authbot_path + 'output.png')
        com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + 'store -i ' + authbot_path + "output.png -m '" + js + "'" + " --room '" + report_room + "'"
        retval = store_challenge(cs)
        print(com)
        try:
            ret = subprocess.check_output(com, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error launching matrix-commander")
            print(e.output)
            return False
        return True

# importing matrix_commander module
try:
    # if installed via pip
    import matrix_commander  # nopep8 # isort: skip
    from matrix_commander import (
        main,
    )  # nopep8 # isort: skip
except:
    # if not installed via pip. if installed via 'git clone' or file download
    # appending a local path to sys.path
    sys.path.append("./matrix_commander")
    sys.path.append("../matrix_commander")
    # print(f"Expanded path is: {sys.path}")
    import matrix_commander  # nopep8 # isort: skip
    from matrix_commander import (
        main,
    )  # nopep8 # isort: skip
########################################################### For systemd debugging...
# For systemd debugging purposes. Redirect stdout to log file to see print statements.
#old_stdout = sys.stdout
#log_file = open("/home/user/authbot/authbot.log","w")
#sys.stdout = log_file
###########################################################
# Read config file and initialize variables...
authbot_path = os.getenv("authbot_path")
with open(authbot_path + 'authbot.json') as f:
    data = json.load(f)

for x in data['params']:
    vars()[x] = data['params'][x]

id_number = 0
print("Checking to see if matrix-commander is running...")

r = commander_up()
# Room to process digital signing...
### Currently supports two digital ids. One public facing id, the other an anonymous id.
### id_number = 0 is the public facing id
### id_number = 1 is the anonymous id
### Rooms are intended to be private matrix protocol rooms
# string to search in file
message_type = 'signature_verification'
with open(message_capture_file, 'r') as fp:
    # read all lines in a list
    lines = fp.readlines()
    for line in lines:
        print("about to call: process_signature_verification...")
        sr = process_signature_verification(line, message_type, room_addr,id_number)
        sr = process_id_lookup(line,"id?",room_addr, id_number) 
        sr = process_json_message(line, "resource_mgr_id", room_addr,id_number)
        sr = process_version(line,"version?",room_addr, id_number) 
        r = commander_up()
fp.close()
########################################################### For systemd debugging...
# For systemd debugging purposes.
#sys.stdout = old_stdout
#log_file.close()
###########################################################
