#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import requests
import sqlite3
import secrets

def remove_request(resource_mgr_id: str, resource_id: str, action: str):
	dbconnect = sqlite3.connect(authbot_path + "authbot")
	cursor = dbconnect.cursor()
	sql = "DELETE FROM request WHERE resource_mgr_id = '" + resource_mgr_id + "' AND resource_id ='" + resource_id + "' AND action = '" + action + "'"
	try:
		cursor.execute(sql)
		dbconnect.commit()
		cursor.close()
		dbconnect.close()
		return True
	except:
		cursor.close()
		dbconnect.close()
		print("Problem deleting challenge_request from database.")
		return False

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
    room = os.environ.get('ENO_ROOM')
    sender = os.environ.get('ENO_SENDER')
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

#    if sender != authbot_owner:
#        print(sender + " your not authorized!")
#        exit(0)

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

    retval = remove_request(buffer['params']['resource_mgr_id'], buffer['params']['resource_id'], buffer['params']['action'])

#    print("TESTING:")
#    print(buffer)
    challenge = buffer['params']['challenge_string']
    id = buffer['params']['controller_id']
#    print(challenge)
    signature = sign(challenge,id,0)
    mjs = '{"json":"2.0","method":"mpsv","params":{"signature":"' + signature + '"'
    retval = generate_json(buffer,mjs)
#    print(retval)
    msg = buffer['params']['resource_mgr_id'] + " mpsv " + retval
    try:
        msg_room = buffer['params']['room_id']
    except:
        msg_room = room
    if msg_room != room: # IF the ENO_ROOM is NOT the room_id specified in the message, use the message specified room_id
        room = msg_room
#    print("OUTPUT:")
#    print(msg)
#    exit(1)
    com = "/home/user/.local/bin/matrix-commander --credentials /home/user/authbot/credentials.json --store /home/user/authbot/store -m '" + msg + "'" + " --room '" + room + "'"
    try:
        ret = subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error launching matrix-commander")
        print(e.output)
        exit(1)
