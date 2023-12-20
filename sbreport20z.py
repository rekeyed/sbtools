#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from time import sleep

bus = SMBus(1)
dev_addr = 0x0b
#bus.enable_pec()
unseal_key_1 = 0x0414
unseal_key_2 = 0x3672

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
    0x19 : ('Design voltage', 2, 'mV'),
    0x3c : ('VCell4', 2, 'mV'),
    0x3d : ('VCell3', 2, 'mV'),
    0x3e : ('VCell2', 2, 'mV'),
    0x3f : ('VCell1', 2, 'mV')
}
hw_report = {
    0x0001 : 'Device type: ',
    0x0002 : 'Firmware ver:',
    0x0003 : 'Hardware ver:',
    0x0008 : 'Chemistry ID:',
    0x0051 : 'Safety status:',
    0x0053 : 'PFStatus:',
    0x0069 : 'Safety status 2:',
    0x006b : 'PFStatus 2:',
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
oper_stat_flags = {
  15 : 'PRES',
  14 : 'FAS',
  13 : 'SS',
  12 : 'CSV',
  10 : 'LDMD',
  7  : 'WAKE',
  6  : 'DSG',
  5  : 'XDSG',
  4  : 'XDSGI',
  2  : 'R_DIS',
  1  : 'VOK',
  0  : 'QEN'
}
manuf_stat_flags = {
   15 : 'FET1',
   14 : 'FET0',
   13 : 'PF1',
   12 : 'PF0',
   11 : 'STATE3',
   10 : 'STATE2',
   9  : 'STATE1',
   8  : 'STATE0'
}
batt_mode_flags = {
    15 : 'CapM',
    14 : 'ChgM',
    13 : 'AM',
    9  : 'PB',
    8  : 'CC',
    7  : 'CF',
    1  : 'PBS',
    0  : 'ICC'
}
fet_control_flags = {
4 : 'OD',
3 : 'ZVCHG',
2 : 'CHG',
1 : 'DSG'
}

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

for key, value in hw_report.items():
    data = smbus_read_wordaddr(bus, dev_addr, key)
    print('{0} 0x{1:04x}'.format(value, data))

data = bus.read_word_data(dev_addr, 0x16)
print('Battery Status: ', '0x{0:04x}\n{1}'.format(data, getflags(data, batt_stat_flags)))

data = smbus_read_wordaddr(bus, dev_addr, 0x0006)
print('Manufacturer Status: ', '0x{0:04x}\n{1}'.format(data, getflags(data, manuf_stat_flags)))

data = smbus_read_wordaddr(bus, dev_addr, 0x0054)
print('Operation Status: ', '0x{0:04x}\n{1}'.format(data, getflags(data, oper_stat_flags)))
if (data & (1 << 13)):
    print("Sealed, trying to unseal...", end='')
    bus.write_word_data(dev_addr, 0, unseal_key_1)
    bus.write_word_data(dev_addr, 0, unseal_key_2)
data = smbus_read_wordaddr(bus, dev_addr, 0x0054)
if (data & (1 << 13)):
    print("Failed")
else:
    print("Unsealed")
    data = smbus_read_subclass(bus, dev_addr, 82, 0x78)
    print("Update Status: ", data[12])
    print("Qmax Cell0: ", data[0]*256+data[1])
    print("Qmax Cell1: ", data[2]*256+data[3])
    print("Qmax Cell3: ", data[4]*256+data[5])
    print("Qmax Cell4: ", data[6]*256+data[7])
    print("Qmax Pack : ", data[8]*256+data[9])

bus.write_word_data(dev_addr, 0x46, 0x0006)
data = bus.read_word_data(dev_addr, 0x46)
print('FET Control: ', '0x{0:04x}\n{1}'.format(data, getflags(data, fet_control_flags)))
bus.close()
