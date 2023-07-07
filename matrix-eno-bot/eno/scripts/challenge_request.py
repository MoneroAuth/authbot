#!/usr/bin/env python3
# This command is for Resource Managers.
import os
import subprocess
import sys
import json
import requests
import sqlite3
import secrets

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
#    print("js: " + js)
    buffer = json.loads(js)

    with open('/home/user/matrix-eno-bot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]
    resource_mgr_id = buffer['params']['resource_mgr_id']
    resource_id = buffer['params']['resource_id']
    authorized_id = buffer['params']['controller_id']
    action = buffer['params']['action']
    room_id = buffer['params']['room_id']
    #print("resource_mgr_id: " + resource_mgr_id)
    if resource_mgr_id != '498EM2vdJRSV6LcRUadS7TE4BdpusMz4wWMAm8YoBAw3M8D3ZkdvYSQN42FBm1aG7X8pRkEFpgvZBPAh78xbYLnj1NZbgJD':
        response = "I am not the appropriate resource manager!"
        print(response)
        exit(1)
#            print("resource_id: " + resource_id)
#            print("authorized_id: " + authorized_id)
#            print("action: " + action)

    dbconnect = sqlite3.connect("/home/user/matrix-eno-bot/eno/scripts/resource_mgr")
    cursor = dbconnect.cursor()

# execute SQL query using execute() method.
    sql = "SELECT a.resource_mgr_id, b.action, c.authorized_id FROM resource a, resource_action b, authorization c WHERE "
    sql = sql + "a.resource_id = b.resource_id And a.resource_id = c.resource_id And c.authorized_id = '"+ authorized_id
    sql = sql + "' And b.action = '" + action + "'"
    #print("sql statement: " + sql)
    count = cursor.execute(sql)
    rs = cursor.fetchone()
    if rs == None:
        print('Authentication failed!')
        cursor.close()
        dbconnect.close()
        exit(1)
# disconnect from server
    else:
        cursor.close()
        dbconnect.close()

        challenge = str(secrets.randbelow(100000000))
        #print("Sending challenge string: " + challenge)
        challenge_msg = '{"json":"2.0","method":"mpc","params":{"challenge_string":"' + challenge + '"'
        buffer = json.loads(js)
        challenge_msg = generate_json(buffer,challenge_msg)
        challenge_message = json.dumps(challenge_msg)
        #print("challenge message: " + challenge_message)
        dbconnect = sqlite3.connect("/home/user/matrix-eno-bot/eno/scripts/resource_mgr")
        cursor = dbconnect.cursor()
        sql = "INSERT INTO challenge(challenge_string,id) VALUES('" + challenge + "','" +authorized_id +"')"
        #print(sql)
        cursor.execute(sql)
        dbconnect.commit()
        cursor.close()
        dbconnect.close()
        msg = buffer['params']['controller_id'] + " mpc " + challenge_msg
        com = matrix_commander_path + "matrix-commander --credentials /home/user/matrix-commander/credentials.json --store /home/user/matrix-commander/store -m '"
        com = com + msg + "'" + " --room '" + room_id + "'"
        try:
            ret = subprocess.check_output(com, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error launching matrix-commander")
            print(e.output)
            exit(1)
