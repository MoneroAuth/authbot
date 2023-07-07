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
    room = os.environ.get('ENO_ROOM')
    sender = os.environ.get('ENO_SENDER')
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

    if sender != authbot_owner:
        print(sender + " your not authorized!")
        exit(0)
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
#    exit(0)
    buffer = json.loads(js)
#    print(buffer)
#    exit(0)

    resource_mgr_id = buffer['params']['resource_mgr_id']
    resource_id = buffer['params']['resource_id']
    authorized_id = buffer['params']['controller_id']
    action = buffer['params']['action']
    try:
        room_id = buffer['params']['room_id']
    except:
        room_id = room
    bot_id = buffer['params']['bot_id']

    dbconnect = sqlite3.connect(authbot_path + "authbot")
    cursor = dbconnect.cursor()

# execute SQL query using execute() method.
    sql = "INSERT INTO request(resource_mgr_id,resource_id,action) VALUES('" + resource_mgr_id + "','" + resource_id + "','" + action + "')"
    try:
        cursor.execute(sql)
        dbconnect.commit()
        cursor.close()
        dbconnect.close()
    except:
        cursor.close()
        dbconnect.close()
        print("Something Happened In Transition (SHIT)")
#    exit(0)
    
    msg = buffer['params']['resource_mgr_id'] + " mpcr " + js
    com = matrix_commander_path + "matrix-commander --credentials " + authbot_path + "credentials.json --store " + authbot_path + "store -m '"
    com = com + msg + "'" + " --room '" + room_id + "'"
#    print(msg)
#    exit(0)
    try:
        ret = subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error launching matrix-commander")
        print(e.output)
        exit(1)
