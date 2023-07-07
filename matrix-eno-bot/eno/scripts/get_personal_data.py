#!/usr/bin/env python3

"""get_personal_data"""

import sys
import json
import sqlite3

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
    print(buffer)
