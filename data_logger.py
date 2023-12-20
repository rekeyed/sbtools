#!/usr/bin/python3

import smbus2
import datetime
from time import sleep
from smb_funcs import *

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
    0x0a : ('Current', 6, 'mA'),
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

def print_log(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, **kwargs, file=logfile)

def get_current(bus, addr):
    curr = smbus_read_word(bus, addr, 0x0a)
    return (curr - 0x10000) if (curr >> 15) else curr

def get_temperature(bus, addr):
    data = smbus_read_word(bus, addr, 0x08)
    return (data * .1 - 273.15)

def get_vcell(bus, addr):
    vcell = []
    for i in range(0x3c, 0x3f + 1):
        vcell.insert(0, smbus_read_word(bus, addr, i))
    return vcell

now = datetime.datetime.now()
logfile_name = 'log_' + now.strftime("%d-%m-%Y_%H-%M-%S") + '.txt'
print("Opening log file", logfile_name, 'for writing...', end='')
try:
    logfile = open(logfile_name, 'w')
except err as error:
    print("Error!")
    print(err)
    exit()
print("OK")

for key, value in sbs_report.items():
    if (value[1] == 1):
        data = smbus_read_block(bus, dev_addr, key)
        data = bytes(data).decode('ascii')
    if (value[1] > 1):
        data = smbus_read_word(bus, dev_addr, key)
    if (value[1] == 3):
        data = str (data & 0x1f) + '.' + str(data >> 5 & 0xf) + '.' + str(1980 + (data >> 9))
    if (value[1] == 4):
        data = '0x{0:04x}'.format(data)
    if (value[1] == 5):
        data = '{0:0.1f}'.format(data * .1 - 273.15)
    if (value[1] == 6):
        data = data - 0x10000 if (data >> 15) else data
    print_log(value[0] + ':', data, value[2])

vcell = get_vcell(bus, dev_addr)
for i in range(0,4):
    print_log('Cell {0} voltage: {1} mV'.format(i, vcell[i]))
data = smbus_read_word(bus, dev_addr, 0x16)
bs = list()
for key, value in batt_stat.items():
    if (data & (1 << key)):
        bs.append(value)
print_log('Battery Status: ', '0x{0:04x}\n'.format(data), ' | '.join(bs))
print("\nConnect load or charger...")
current = 0
while (current == 0):
    sleep(0.2)
    current = get_current(bus, dev_addr)
sleep(0.5)
current = get_current(bus, dev_addr)
if current > 0:
    print_log('Charger detected. ', end ='')
else:
    print_log('Load detected. ', end='')
print_log('Current = {} mA'.format(abs(current)))
v = get_vcell(bus, dev_addr)
for i in range(0,4):
    r = (v[i] - vcell[i]) / current * 1000
    print_log('Cell {0} voltage: {1} mV  R={2:.1f} mOhm'.format(i, v[i], r))
start_time = datetime.datetime.now()
prev_time = 0
capacity = 0
print_log("Log started:", start_time)
start_time = start_time.timestamp()
print("\nTime,Current,Voltage,Vcell0,Vcell1,Vcell2,Vcell3,Temperature,RemainingCapacity,CapacityPassed", file=logfile)
while (current != 0):
    time_passed = datetime.datetime.now().timestamp() - start_time
    current = get_current(bus, dev_addr)
    voltage = smbus_read_word(bus, dev_addr, 0x09)
    t = get_temperature(bus, dev_addr)
    rem_cap = smbus_read_word(bus, dev_addr, 0x0f)
    vcell = get_vcell(bus, dev_addr)
    capacity += (time_passed - prev_time) * current / 3600
    prev_time = time_passed
    print("{:.2f},{},{},{},{},{},{},{:.1f},{},{:.1f}".format(
        time_passed, current, voltage, vcell[0], vcell[1], vcell[2], vcell[3], t, rem_cap, capacity), file=logfile)
    print("Time={:.1f}s, I={}mA, V={}mV, V0={}, V1={}, V2={}, V3={}, T={:.1f}\xb0C, RemCap={}, Cap={:.1f}mAh     ".format(
        time_passed, current, voltage, vcell[0], vcell[1], vcell[2], vcell[3], t, rem_cap, capacity), end='\r')
    if (int(time_passed) % 300 <= 1):
        print()
    sleep(1)
print_log('\nLog ended:', datetime.datetime.now())
bus.close()
