#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from smb_funcs import *
from time import sleep
from basic_report import *

bus = SMBus(1)
dev_addr = 0x0b
#bus.enable_pec()
unseal_key_1 = 0x0414
unseal_key_2 = 0x3672

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

def getflags(data, flags):
    stat = list()
    for key, value in flags.items():
        if (data & (1 << key)):
            stat.append(value)
    if (stat):
        return '|'.join(stat)
    return 'No flags set'

print_basic_report(bus, dev_addr)

for key, value in hw_report.items():
    data = smbus_read_wordaddr(bus, dev_addr, key)
    print('{0} 0x{1:04x}'.format(value, data))

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
