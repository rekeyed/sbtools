#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from time import sleep

def smbus_read_block(bus, addr, cmd):
    max_error = 10
    success = 0
    while (success == 0):
        try:
            length = bus.read_byte_data(addr, cmd)
            write = i2c_msg.write(addr, [cmd])
            read = i2c_msg.read(addr, length + 1)
            bus.i2c_rdwr(write, read)
            data = list(read)
            success = 1
        except:
            max_error -= 1
            if (max_error == 0):
                print("\nSorry, maximum error count reached while reading SMBus(block)")
                exit(1)
            sleep(.1)
    return (data[1:])

def smbus_read_word(bus, addr, cmd):
    max_error = 10
    success = 0
    while (success == 0):
        try:
            data = bus.read_word_data(addr, cmd)
            success = 1
        except:
            max_error -= 1
            if (max_error == 0):
                print("\nSorry, maximum error count reached while reading SMBus")
                exit(1)
            sleep(.1)
    return (data)

def smbus_read_subclass(bus, addr, id, page):
    bus.write_word_data(addr, 0x77, id)
    sleep(0.1)
    data = smbus_read_block(bus, addr, page)
    #print ('subclass 0x{0:02x}, page=0x{1:02x}, len={2}:'.format(id, page, len(data)), ''.join("{:02x}".format(num) for num in data))
    return data

def smbus_read_wordaddr(bus, addr, word):
    bus.write_word_data(addr, 0, word)
    return bus.read_word_data(addr, 0)