#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from time import sleep

bus = SMBus(1)
dev_addr = 0x0b
#bus.enable_pec()

bus.write_word_data(dev_addr, 0, 0x0021)
bus.close()
