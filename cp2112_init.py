#!/usr/bin/env python3

import time
import hid

bus_speed = 40000   # Bus speed in Hz
write_timeout = 100 # 0-1000ms, 0 - disabled
read_timeout = 100  # 0-1000ms, 0 - disabled
retry_count = 10    # 0-1000, 0 - No limit

# read AN495: CP2112 Interface Specification for details
print("Start initialization")
h = hid.device()
h.open(0x10C4, 0xEA90, None) # Connect HID again after enumeration
print("Manufacturer: %s" % h.get_manufacturer_string())
print("Product: %s" % h.get_product_string())
print("Serial No: %s" % h.get_serial_number_string())
h.send_feature_report([0x02, 0x83, 0xff, 0xff, 0x01])  # initialize GPIO and TX/RX led
data = h.get_feature_report(0x05, 3)
print ('Part No: 0x{:02x}, version: 0x{:02x}'.format(data[1], data[2]))
# Set bus speed, device address, write and read timeouts
print ('Set bus speed to {} kHz, write timeout to {} ms, read timeout to {} ms'.format(
    bus_speed // 1000, write_timeout, read_timeout))
h.send_feature_report([0x06, # report ID
    bus_speed >>24 & 0xff, bus_speed >> 16 & 0xff, bus_speed >> 8 & 0xff, bus_speed & 0xff, # Bus speed
    0x02, # device address, shifted
    0x00, # Auto Send Read (0 - disabled)
    write_timeout >> 8 & 0xff, write_timeout & 0xff, # Write Timeout
    read_timeout >> 8 & 0xff, read_timeout & 0xff, # Read Timeout
    0x00, # SCL Low Timeout (0 - disabled)
    retry_count >> 8 & 0xff, retry_count & 0xff]) # Retry Time
h.close()
