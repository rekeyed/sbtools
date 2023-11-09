#!/usr/bin/python3

import smbus2

bus = smbus2.SMBus(1)
dev_addr = 0x0b
#bus.enable_pec()

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
    0x0f : ('Remaining capacity', 2, 'mAh'),
    0x10 : ('Full charge capacity', 2, 'mAh'),
    0x14 : ('Charging Current', 2, 'mAh'),
    0x15 : ('Charging Voltage', 2, 'mV'),
    0x17 : ('Cycle count', 2, ''),
    0x18 : ('Design capacity', 2, 'mAh'),
    0x19 : ('Design voltage', 2, 'mV')
}
batt_stat = {
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

def  smbus_read_block(bus, addr, cmd):
    length = bus.read_byte_data(0x0b, cmd)
    if length > 31:
        length = 31
    data = bus.read_i2c_block_data(0x0b, cmd, length + 1)
    return (data[1:])

for key, value in sbs_report.items():
    if (value[1] == 1):
        data = smbus_read_block(bus, dev_addr, key)
        data = bytes(data).decode('ascii')
    if (value[1] > 1):
        data = bus.read_word_data(dev_addr, key)
    if (value[1] == 3):
        data = str (data & 0x1f) + '.' + str(data >> 5 & 0xf) + '.' + str(1980 + (data >> 9))
    if (value[1] == 4):
        data = '0x{0:04x}'.format(data)
    if (value[1] == 5):
        data = '{0:0.1f}'.format(data * .1 - 273.15)
    print(value[0] + ':', data, value[2])
data = smbus_read_block(bus, dev_addr, 0x23)
if (len(data) >= 12):
    for i in range(0,4):
        print('Cell {0} voltage: {1} mV'.format(i, data[4 + i * 2 ] + data[4 + i * 2 + 1] * 256))
data = bus.read_word_data(dev_addr, 0x16)
bs = list()
for key, value in batt_stat.items():
    if (data & (1 << key)):
        bs.append(value)
print('Battery Status: ', '0x{0:04x}\n'.format(data), ' | '.join(bs))
bus.close()
