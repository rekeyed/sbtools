#!/usr/bin/python3

import smbus2

bus = smbus2.SMBus(1)
dev_addr = 0x0b
#bus.enable_pec()

bus.write_byte(dev_addr, 0x08)
bus.close()
