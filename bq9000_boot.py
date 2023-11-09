#!/usr/bin/python3

import smbus2, random

bus = smbus2.SMBus(1)
dev_addr = 0x0b

bus.write_word_data(dev_addr, 0x71, 0x0214)
data74 = bus.read_word_data(dev_addr, 0x74)
i = 0
count = 0
while(1):
    count += 1
    data = bus.read_word_data(dev_addr, 0x73)
    bus.write_word_data(dev_addr, 0x71, i)
    print('{:10} data 74: 0x{:04x}, challenge: 0x{:04x}, guess: 0x{:04x} - '.format(count, data74, data, i), end='')
    try:
        bus.write_word_data(dev_addr, 0x70, 0x0517)
        print('OK')
        break
    except:
        print('Failed')
    i = random.randint(0, 0xffff)
bus.close()
