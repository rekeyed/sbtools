#!/usr/bin/python3

import smbus2
from basic_report import *

bus = smbus2.SMBus(1)
dev_addr = 0x0b
#bus.enable_pec()

print_basic_report(bus, dev_addr)

bus.close()
