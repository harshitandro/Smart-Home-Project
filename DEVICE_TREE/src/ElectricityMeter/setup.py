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

import machine
import btree

conf = open("conf.txt", "r")
try:
    f = open("conf", "r+b")
except OSError:
    f = open("conf", "w+b")
db = btree.open(f)


def run():
    irq_state = machine.disable_irq()
    for line in conf.readlines():
        line = line.strip("\n").split(":")
        global db
        db[bytes(bytearray(line[0]))] = bytes(bytearray(line[1]))
        db.flush()
        f.flush()
    machine.enable_irq(irq_state)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('SmartHomeNetwork', 'skitsmarthome')
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    time.sleep(3)


def close():
    db.close()
    f.close()
    conf.close()
    import os
    os.remove("conf.txt")
