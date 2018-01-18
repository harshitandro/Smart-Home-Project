# The Database module from handling all the database request from the server

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

try:
    db_connection = db_connector.connect(**db_config)
    db_connection.set_autocommit(True)
    if db_connection.is_connected():
        print("Connected to DB")
except db_connector.Error as err:
    print(err)

def getCursor():
    return db_connection.cursor()

def createAcc(uid,typ):
    db_cursor = getCursor()
    try:
        db_cursor.execute("CREATE TABLE {}_{}_usage ("
                           "total_usage DOUBLE NOT NULL,"
                           "log_time TIMESTAMP NOT NULL UNIQUE"
                           ");".format(uid,typ))
        print("New Account created for : ", uid)
    except Error as err:
        print("Error creating account for : ",uid)
        print("Error : ", err)

def closeConnection():
    db_connection.close()
