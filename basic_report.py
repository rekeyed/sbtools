#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from time import sleep


def smbus_read_block(bus, addr, cmd):
    length = bus.read_byte_data(addr, cmd)
    write = i2c_msg.write(addr, [cmd])
    read = i2c_msg.read(addr, length + 1)
    bus.i2c_rdwr(write, read)
    data = list(read)
    return (data[1:])

def smbus_read_subclass(bus, addr, id, page):
    bus.write_word_data(addr, 0x77, id)
    sleep(0.1)
    data = smbus_read_block(bus, addr, page)
    print ('subclass 0x{0:02x}, page=0x{1:02x}, len={2}:'.format(id, page, len(data)), ''.join("{:02x}".format(num) for num in data))
    return data

def getflags(data, flags):
    stat = list()
    for key, value in flags.items():
        if (data & (1 << key)):
            stat.append(value)
    if (stat):
        return '|'.join(stat)
    return 'No flags set'

def smbus_read_wordaddr(bus, addr, word):
    bus.write_word_data(addr, 0, word)
    return bus.read_word_data(addr, 0)

def print_basic_report(bus, dev_addr):
    sbs_report = {
        0x20 : ('Manufacturer Name', 1, ''),
        0x21 : ('Device Name', 1, ''),
        0x22 : ('Device Chemistry', 1, ''),
        0x1c : ('Serial Number' , 2, ''),
        0x1b : ('Mfd Date', 3, ''),
        0x00 : ('Manufacturer access' , 4, ''),
        0x01 : ('Remaining capacity alarm', 2, 'mAh'),
        0x02 : ('Remaining time alarm', 2, 'min'),
        0x03 : ('Battery mode', 4, ''),
        0x08 : ('Temperature', 5, '\xb0C'),
        0x09 : ('Voltage', 2, 'mV'),
        0x0a : ('Current', 2, 'mA'),
        0x0c : ('Max error', 2, '%'),
        0x0d : ('RSoC', 2, '%'),
        0x0e : ('ASoC', 2, '%'),
        0x0f : ('Remaining capacity', 2, 'mAh'),
        0x10 : ('Full charge capacity', 2, 'mAh'),
        0x14 : ('Charging Current', 2, 'mAh'),
        0x15 : ('Charging Voltage', 2, 'mV'),
        0x17 : ('Cycle count', 2, ''),
        0x18 : ('Design capacity', 2, 'mAh'),
        0x19 : ('Design voltage', 2, 'mV'),
        0x3c : ('VCell3', 2, 'mV'),
        0x3d : ('VCell2', 2, 'mV'),
        0x3e : ('VCell1', 2, 'mV'),
        0x3f : ('VCell0', 2, 'mV')
    }
    batt_stat_flags = {
        4 : 'FD',
        5 : 'FC',
        6 : 'DSG',
        7 : 'INIT',
        8 : 'RTA',
        9 : 'RCA',
        11 : 'TDA',
        12 : 'OTA',
        14 : 'TCA',
        15 : 'OCA'
   }

    for key, value in sbs_report.items():
        if (value[1] == 1):
            data = smbus_read_block(bus, dev_addr, key)
            data = bytes(data).decode('ascii')
        if (value[1] > 1):
            data = bus.read_word_data(dev_addr, key)
        if (value[1] == 3):
            data = '{:02}.{:02}.{}'.format(data & 0x1f, data >> 5 & 0xf, (data >> 9) + 1980)
        if (value[1] == 4):
            data = '0x{0:04x}'.format(data)
        if (value[1] == 5):
            data = '{0:0.1f}'.format(data * .1 - 273.15)
        print(value[0] + ':', data, value[2])
    data = smbus_read_block(bus, dev_addr, 0x23)
    print('ManufacturerData:', ' '.join(['{:02x}'.format(i) for i in data]))
    data = bus.read_word_data(dev_addr, 0x16)
    print('Battery Status:', '0x{0:04x}\n{1}'.format(data, getflags(data, batt_stat_flags)))

