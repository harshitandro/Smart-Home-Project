# The Water Meter Device module

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

from machine import Pin
from machine import PWM
from machine import Timer
from socket import *
import network
import time
import micropython
import machine
import btree
import os

micropython.alloc_emergency_exception_buf(100)

if "conf.txt" in os.listdir():
    import setup

    setup.run()
    setup.close()

import remote_sender

try:
    f = open("conf", "r+b")
except OSError:
    f = open("conf", "w+b")
db = btree.open(f)
irq_state = machine.disable_irq()
global listen_port
listen_port = int(str(db[b"listen_port"], "utf-8"))
global calib
calib = float(str(db[b"calib"], "utf-8"))

db.close()
f.close()
machine.enable_irq(irq_state)


class WaterMeter:
    def __init__(self):
        # machine.freq(160000000)
        try:
            self.f = open("conf", "r+b")
        except OSError:
            self.f = open("conf", "w+b")
        self.db = btree.open(self.f)
        self.COUNTER = 0
        self.INSTANT_FLOW = 0.0
        self.LED_PIN_NUMBER = 4  # D2		# indicator LED Connection
        self.SENSOR_PIN_NUMBER = 5  # D1		# data connection to sensor
        self.GLOBAL_COUNTER = 0.0
        try:
            self.GLOBAL_COUNTER = float(str(self.db[b"GLOBAL_COUNTER"], "utf-8"))
        except KeyError:
            self.GLOBAL_COUNTER = 0.0
        self.led = Pin(self.LED_PIN_NUMBER)
        self.led = PWM(self.led)
        self.sensor = Pin(self.SENSOR_PIN_NUMBER, Pin.IN, Pin.PULL_UP)
        self.timer = Timer(-1)
        self.led.duty(512)
        self.led.freq(1)
        self.sensor.irq(trigger=Pin.IRQ_RISING, handler=self.counter)
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self.update_global)

    def led_control(self, count):
        if count == 0:
            self.led.duty(0)
        else:
            self.led.duty(512)
        self.led.freq(int(count * 20))

    def counter(self, pin):
        self.COUNTER += 1

    def update_global(self, loc):
        self.INSTANT_FLOW = (self.COUNTER * calib)
        self.GLOBAL_COUNTER = self.GLOBAL_COUNTER + self.INSTANT_FLOW
        self.COUNTER = 0
        self.led_control(self.INSTANT_FLOW)
        irq_state = machine.disable_irq()
        self.db[b"GLOBAL_COUNTER"] = bytes(str(self.GLOBAL_COUNTER), "utf-8")
        self.db.flush()
        self.f.flush()
        machine.enable_irq(irq_state)

    def getVal(self):
        return str(self.GLOBAL_COUNTER)


if __name__ == "__main__":
    meter = WaterMeter()
    t1 = Timer(-1)
    t1.init(period=10000, mode=Timer.PERIODIC, callback=lambda t: remote_sender.send_data(meter.getVal()))
    listen_soc = socket(AF_INET, SOCK_DGRAM)
    local_send_soc = socket(AF_INET, SOCK_STREAM)
    listen_soc.bind(("0.0.0.0", listen_port))
    while True:
        local_send_soc = socket(AF_INET, SOCK_STREAM)
        listen_soc.settimeout(0.5)
        clientFlag = False
        client_address = []
        while not clientFlag:
            try:
                data, client_addr = listen_soc.recvfrom(4096)
                if (str(data, "utf-8").split(":"))[0] == "{}_SERVER_BCAST".format(dev_type):
                    client_address = (client_addr[0], int((str(data, "utf-8").split(":"))[1]))
                    print(client_address[0], client_address[1])
                    local_send_soc.connect(client_address)
                    print("socket connected")
                    clientFlag = True
            except OSError:
                print("Socket Timeout")
        for i in range(5000):
            try:
                local_send_soc.sendall(str.encode(meter.getVal(), encoding='utf-8'))
            except OSError:
                print("Client Disconnected")
                local_send_soc.close()
                clientFlag = False
                break
