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

from socket import *
import btree
import machine
import ubinascii
import uhashlib

try:
    f = open("conf", "r+b")
except OSError:
    f = open("conf", "w+b")
db = btree.open(f)
remote_soc = socket(AF_INET, SOCK_DGRAM)

irq_state = machine.disable_irq()
global uid
uid = str(db[b"uid"], "utf-8")
global secret_hash
secret_hash = str(db[b"secret_hash"], "utf-8")
global dev_type
dev_type = str(db[b"type"], "utf-8")
global server_addr
server_addr = str(db[b"server_addr"], "utf-8")
global server_port
server_port = int(str(db[b"server_port"], "utf-8"))
db.close()
f.close()

machine.enable_irq(irq_state)

server_addr = ((getaddrinfo(server_addr, 23)[0])[4])[0]
print("Remote Sender init complete")


def gen_auth(data=""):
    return str(ubinascii.hexlify(bytearray(uhashlib.sha256(secret_hash + data).digest())), "utf-8")


def send_data(data=""):
    remote_soc.sendto("{};{};{};{}".format(data, uid, dev_type, gen_auth(data)).encode("utf-8"),
                      (server_addr, server_port))
