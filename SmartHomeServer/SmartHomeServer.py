# The Smart Home Server module from handling all the device service request

#                       License
# This file is part of the Smart-Home-Project distribution
# (https://github.com/harshitandro/Smart-Home-Project).
#
# Copyright (c) 2017 Harshit Singh Lodha <harshitandro@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import datetime
import hashlib
import socket
import time
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

import Database
from mysql.connector.errors import Error

recv_sock = None
executor = None
listener_executor = None

# device type defination
dev_type = {
    "wm":"WaterMeter",
    "gm":"GasMeter",
    "em":"ElectricMeter",
    "ss":"SmartSwitch"
}

def __init__(port=9000):
    global recv_sock
    recv_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    recv_sock.bind(("",9000))
    recv_sock.settimeout(1)
    global executor
    executor = ProcessPoolExecutor()
    global listener_executor
    listener_executor = ThreadPoolExecutor(4)

# start the server
def start():
    global  listener_executor
    listener_executor.submit(device_listener)

# listener for the device request
def device_listener():
    while True:
        try:
            data , addr = recv_sock.recvfrom(4096)
            info = str(data,encoding="utf-8").strip().split(";")
            print(info)
            #
            #   Packet format : Value ; UID ; Type ; Secret
            #
            executor.submit(updateDB,info)
        except socket.timeout:
            print("timeout")

# authenticate the device req.  Return true if auth successful
def authenticate(val ,key , secret):
    token_val = key + val
    if secret == hashlib.sha256(bytes(bytearray(token_val,encoding="utf-8"))).hexdigest():
        return True
    return False

# get secret hash from the server using device UID
def getHash(db_cursor,uid):
    try :
        db_cursor.execute("SELECT hash FROM device_info WHERE uid='{}';".format(uid))
        for hash in db_cursor.fetchall():
            return hash[0]
    except Error as err:
        return ""

# database update sequence for authenticated response
def updateDB(info):
    #
    #   Packet format : Value ; UID ; Type ; Secret
    #
    db_cursor = Database.getCursor()
    if authenticate(info[0],getHash(db_cursor,info[1]),info[3]):
        print("auth completed")
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        try :
            db_cursor.execute("select total_usage from {}_{}_usage ORDER BY log_time DESC limit 1;".format(info[1],dev_type[info[2]]))
            for total_usage in db_cursor.fetchall():
                if str(total_usage[0]) != info[0]:
                    db_cursor.execute("INSERT INTO {}_{}_usage VALUES('{}','{}');".format(info[1],dev_type[info[2]],info[0],timestamp))
        except Error as err:
            print(err)
            Database.createAcc(info[1], dev_type[info[2]])
            db_cursor.execute("INSERT INTO {}_{}_usage VALUES('{}','{}');".format(info[1],dev_type[info[2]],info[0],timestamp))
        print("Update Complete")
    else :
        print("Auth failed")

if __name__ == '__main__':
    __init__()
    start()
