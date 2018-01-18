# The Database module to interact with the Smart Home Database Server
# for the Smart Device registration & initialisation.
#

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


import mysql.connector as db_connector
from mysql.connector.errors import Error
from mysql.connector import errorcode

##############################################################################################
#		To be modified by deployer						     #
##############################################################################################
# config for the DB connection
db_config={
    'user': 'db_server_username',
    'password': 'db_server_password',
    'host': 'db_server_hostname',
    'database': 'Smart_Home_DB' # DB Name
}

##############################################################################################


# creates the DB table for device_info
def createDeviceRegister():
    db_cursor = getCursor()
    try:
        db_cursor.execute("CREATE TABLE `device_info` ("
                          "  `uid` varchar(12) NOT NULL,"
                          "  `type` char(2) NOT NULL,"
                          "  `hash` varchar(12) NOT NULL,"
                          "  `cid` varchar(12)  NOT NULL,"
                          "  PRIMARY KEY (`uid`),"
                          "  UNIQUE KEY `uid_UNIQUE` (`uid`),"
                          "  UNIQUE KEY `hash_UNIQUE` (`hash`)"
                          ") ENGINE=InnoDB")
        print("New Device Register created")
    except Error as err:
        print("Error creating new Device Register")
        print("Error : ", err)

# returns db cursor
def getCursor():
    return db_connection.cursor()

# register the device into the Smart Home Server DB
def registerDevice(uid="",dev_type="",hash=None,cid=""):
        db_cursor = getCursor()
        if hash == None:
            print("ERR : Hash Value provided is NULL")
            return -1
        elif uid == "":
            print("ERR : UniqueID Value provided is NULL")
            return -1
        elif cid == "":
            print("ERR : CustomerID Value provided is NULL")
            return -1
        else:
            try:
                db_cursor.execute("INSERT INTO device_info VALUES('{}','{}','{}','{}')".format(uid,dev_type,hash,cid))
                return 0
            except Error as err :
                if err.errno == errorcode.ER_DUP_ENTRY:
                    if err.msg.find(uid) != -1:
                        return "DUP_UID"
                    elif err.msg.find(hash) != -1:
                        return "DUP_HASH"

def closeConnection():
    db_connection.close()

try:
    db_connection = db_connector.connect(**db_config)
    db_connection.set_autocommit(True)
    if db_connection.is_connected():
        print("Connected to DB")
    db_cursor = getCursor()
    db_cursor.execute("SHOW TABLES LIKE 'device_info';")
    if len(db_cursor.fetchall()) == 0:
        createDeviceRegister()
except db_connector.Error as err:
    print(err)

