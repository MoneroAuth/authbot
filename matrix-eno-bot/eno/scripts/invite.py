#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import requests
import sqlite3
import secrets
from datetime import date
from datetime import timedelta
#import random


if __name__ == "__main__":
    line = " ".join(sys.argv[1:])
#    print(line)
    data = line.split()
    n = len(data)
#    print("Number of args provided: " + str(n))
#    print(data[0])
#    print(data[1])
    user = ""
    room = ''
    for g in data:
        if g.find('!') > -1:
#            print("Room ID:" + g)
            room = room + g
        if g.find('@') > -1:
#            print('User:' + g)
            user = user + "'" + g + "'"
            user = user + " "
#    print("invite " + room + " " + user)
#    exit(0)
    with open('/home/user/authbot/authbot.json') as f:
        data = json.load(f)

    f.close()

    for x in data['params']:
        vars()[x] = data['params'][x]

    com = matrix_commander_path + 'matrix-commander --credentials ' + authbot_path + 'credentials.json --store ' + authbot_path + "store --room-invite '" + room + "' --user " + user 
#    print(com)
#    exit(0)
    try:
        ret = subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error launching matrix-commander")
        print(e.output)
        exit(1)
    print("Invited: " + user + "to room: " + room)
