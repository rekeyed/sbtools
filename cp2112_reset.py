#!/usr/bin/env python3

import time
import hid

# read AN495: CP2112 Interface Specification for details
h = hid.device()
h.open(0x10C4, 0xEA90, None) # Connect HID again after enumeration
print("Manufacturer: %s" % h.get_manufacturer_string())
print("Product: %s" % h.get_product_string())
print("Serial No: %s" % h.get_serial_number_string())
h.send_feature_report([0x02, 0x83, 0xff, 0xff, 0x01])  # initialize GPIO and TX/RX led
data = h.get_feature_report(0x05, 3)
print ('Part No: 0x{:02x}, version: 0x{:02x}'.format(data[1], data[2]))
# Set bus speed, device address, write and read timeouts
print ('Reset device...')
h.send_feature_report([0x01, 0x01])
h.close()
