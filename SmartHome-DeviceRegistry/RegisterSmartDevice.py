# The Registration module to interact with the Smart Home Database Server
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

import hashlib
import os
import shutil

import subprocess
from os import urandom
from time import sleep

import Database

DEVICE_PATH = "/dev/ttyUSB0"
DEVICE_BAUD = 115200

##############################################################################################
#		To be modified by deployer						     #
##############################################################################################
DEVICE_TREE_LOC = ""  # location of DEVICE_TREE root
CONTINUE_FLAG = True

# info to be placed in the smart device about the Smart Home Server to upload the data to.
server_info = {
    "server_addr":"URL to the server",
    "server_port":"Port number"
}

device_info = {
    "calib":"calibration value per pulse",
    "listen_port":"Local Broadcast port number"
}
##############################################################################################


# Get UID from connected Smart Device
def get_uid():
    s = subprocess.Popen("esptool.py -p {} -b {} read_mac".format(DEVICE_PATH,DEVICE_BAUD), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in s.stdout.readlines():
        line = str(line.strip(),"utf-8")
        if line.startswith("MAC") :
            mac = line[4:]
            mac = "".join(mac.split(":")).strip()
            return mac

# Generate secret hash for the device auth.
def get_secret_hash():
    return hashlib.sha256(urandom(12)).hexdigest()[:12]

# formats the device for initialisation
def format_device():
    try:
        s = subprocess.Popen("esptool.py -a hard_reset --before default_reset -p {} -b {} erase_flash".format(DEVICE_PATH,DEVICE_BAUD), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sleep(2)
        s = subprocess.Popen("esptool.py -a hard_reset -p {} -b {} erase_flash".format(DEVICE_PATH, DEVICE_BAUD),
                             shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in s.stdout.readlines():
            print("\t>>"+str(line,"utf-8"))
        sleep(2)
        print()
        s = subprocess.Popen("esptool.py -a hard_reset --before default_reset -p {} -b {} write_flash --flash_size=detect 0 {}".format(DEVICE_PATH, DEVICE_BAUD,"{}/firmware/esp_firmware.bin".format(DEVICE_TREE_LOC)), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in s.stdout.readlines():
            print("\t>>"+str(line,"utf-8"))
        sleep(5)
        return True
    except FileNotFoundError:
        return False

# push the source files from $DEVICE_TREE_LOC/src/{dev_type} to the device
def push_src_files(dev_type):
    try:
        for file in os.listdir("{}/src/{}".format(DEVICE_TREE_LOC,dev_type)):
            s = subprocess.Popen("ampy -p {} -b {} put {}".format(DEVICE_PATH, DEVICE_BAUD,"{}/src/{}/{}".format(DEVICE_TREE_LOC,dev_type,file)), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in s.stdout.readlines():
                print("\t>>" + str(line, "utf-8"))
            sleep(2)
        for file in os.listdir():
            s = subprocess.Popen("ampy -p {} -b {} put {}".format(DEVICE_PATH, DEVICE_BAUD,"{}".format(file)), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in s.stdout.readlines():
                print("\t>>" + str(line, "utf-8"))
            sleep(2)
        s = subprocess.Popen("ampy -p {} -b {} reset".format(DEVICE_PATH, DEVICE_BAUD), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True
    except FileNotFoundError:
        return False

if __name__ == '__main__':
    print("Welcome to Smart Device Registerer.")
    DEVICE_TREE_LOC = input("Enter the root location [ABSOLUTE] for  Device Config Files(DEVICE_TREE) :")
    print("Entered Root Location : {}".format(DEVICE_TREE_LOC))
    if not os.path.exists(DEVICE_TREE_LOC):
        print("\tWARNING : Given Root Location doesn't exist.")
        print("Creating given root location")
        os.makedirs(DEVICE_TREE_LOC)
        print()
        print("Entering Device Config Stage :\n")
    os.chdir(DEVICE_TREE_LOC)
    while CONTINUE_FLAG:
        print()
        if input("Press ENTER when device connected !!") == "":
            if not os.path.exists(DEVICE_PATH):
                print("\tERROR : Device not found.")
            dev_id =get_uid()
            if not os.path.exists(dev_id):
                print("\n")
                print("For Device ID : ", end="")
                secret_hash = get_secret_hash()
                print(dev_id)
                print("Secret Key : {}".format(secret_hash))
                dev_type = input("Enter the type of this device (WM,EM or GM ?): ")
                print("Writing to records...")
                os.mkdir(dev_id)
                os.chdir(dev_id)
                code = Database.registerDevice(dev_id,dev_type, secret_hash, "0000")
                while True:
                    if code == 0 :
                        rec = open("conf.txt","w")
                        rec.write("uid:{}\n".format(dev_id))
                        rec.write("secret_hash:{}\n".format(secret_hash))
                        rec.write("type:{}\n".format(dev_type))
                        rec.write("server_addr:{}\n".format(server_info["server_addr"]))
                        rec.write("server_port:{}\n".format(server_info["server_port"]))
			rec.write("listen_port:{}\n".format(device_info["listen_port"]))
			rec.write("calib:{}\n".format(device_info["calib"]))
                        rec.close()
                        print("Flashing the device & populating conf files ...")
                        if not format_device():
                            print("ERROR : Failed to format device")
                            os.chdir(os.pardir)
                            break
                        if push_src_files(dev_type) :
                            print("Done.")
                        else :
                            print("ERROR : Failed to copy src files to device")
                        os.chdir(os.pardir)
                        break
                    elif code == "DUP_UID":
                        print("\tERROR : Device already registered.")
                        os.chdir(os.pardir)
                        os.removedirs(dev_id)
                        break
                    elif code == "DUP_HASH":
                        secret_hash = get_secret_hash()
                        code = Database.registerDevice(dev_id, dev_type,secret_hash, "0000")
                    elif code == -1:
                        print("\tERROR : Invalid Parameters")
                        os.chdir(os.pardir)
                        os.removedirs(dev_id)
                        break


            else:
                print("\tERROR : Device Config files already exists.")
        if input("Want to register more devices ( y/N ) : ") not in ['y','Y']:
            CONTINUE_FLAG = False



