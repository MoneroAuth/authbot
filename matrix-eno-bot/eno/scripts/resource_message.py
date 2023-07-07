#!/usr/bin/env python3

import subprocess
import sys
import json
import requests
import sqlite3
import secrets
import hashlib

def verify_signature(challenge: str, id: str, signature: str):

	url = "http://127.0.0.1:18089/json_rpc"
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
	#print(retval)
	if retval:
		return True
	else:
		return False

if __name__ == "__main__":
    line = " ".join(sys.argv[1:])
    jbx = line.find('{"json')
    jex = line.find("}}",jbx)
    js = line[jbx:jex+2]
    #print("json message: " + js)
# Put the commas back!
    x = js.replace(" ", ",")
    js = x
    buffer = json.loads(js) 
    challenge = buffer['params']['challenge_string']
    #print("challenge_string: " + challenge)
    id = buffer['params']['id']
    #print("id: " + id)
    signature = buffer['params']['signature']
    #print("signature: " + signature)
    retval = verify_signature(challenge, id, signature)
    if retval:
        #print("signature verified!")
        t = True
    else:
        print("Invalid signature!")
        exit(1)
# Check to make sure we don't have any message reuse...
    dbconnect = sqlite3.connect("/home/user/moneroauth/data.db")
    dbconnect.row_factory = sqlite3.Row
    cursor= dbconnect.cursor()
    cursor.execute("SELECT action, issued FROM command_history WHERE action = '" + js + "'")
    for row in cursor:
        #print(row['action'], row['issued'])
        print("Reuse Detected. Ignoring message!")
        cursor.close()
        dbconnect.close()
        exit(1)
    cursor.close()
    dbconnect.close()
# Do action
    action = buffer['params']['action']
#    print("action: " + action)
    dbconnect = sqlite3.connect("/home/user/moneroauth/data.db")
    cursor= dbconnect.cursor()
    if action == 'get_personal_data':
        sql = "select data FROM action WHERE action = '" + action + "'"
 #   print(sql)
        cursor.execute(sql)
        record = cursor.fetchone()
 #       print(record[0])
        msg = record[0]
        cursor.close()
        dbconnect.close()
    if action == 'update_personal_data':
# Store the updated data in the database...
        dataset = buffer['params']['dataset']
        ds = str(dataset).replace("'",'"')
        #print(ds)
        sql = "Update action SET data = '" + ds + "'"
        cursor.execute(sql)
        cursor.commit()
        cursor.close()
        dbconnect.close()
#        print("Personal data set updated.")
        msg = "Personal data set updated"


# Record in command_history...
    dbconnect = sqlite3.connect("/home/user/moneroauth/data.db")
#    dbconnect.row_factory = sqlite3.Row
    cursor= dbconnect.cursor()
    sql = "INSERT INTO command_history (action) VALUES('" + js + "')"
    #print("sql statement: " + sql)
    count = cursor.execute(sql)
    dbconnect.commit()
    cursor.close()
    dbconnect.close()

# Send status message...
    report_room = buffer['params']['room_id']
    msg = buffer['params']['controller_id'] + " echo " + msg
#    print("OUTPUT:")
#    print(msg)
#    exit(1)
    com = "/home/user/.local/bin/matrix-commander --credentials /home/user/authbot/credentials.json --store /home/user/authbot/store -m '" + msg + "'" + " --room '" + report_room + "'"
    try:
        ret = subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error launching matrix-commander")
        print(e.output)
        exit(1)
