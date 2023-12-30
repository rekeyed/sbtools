#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from smb_funcs import *
from time import sleep
from basic_report import *
from pprint import pprint

bus = SMBus(1)
dev_addr = 0x0b

def sbs_read_firmware_version_bq_sealed(bus, dev_addr):
    """ Reads firmware version from BQ series chips

    https://github.com/o-gs/dji-firmware-tools/blob/master/comm_sbs_bqctrl.py#L2767
    Uses the sequence which allows to read the FW version even in sealed mode.
    The sequence used to do this read requires low-level access to the bus via
    i2c commands which allows sending raw data. Not all smbus wrappers
    available in various platforms have that support.
    """

    # Do 3 commands which pretend to write oversized buffer; this needs to be done within 4 seconds
    for pre_cmd in (0x22, 0x20, 0x22):
        # We are sending messages which are not correct commands - we expect to receive no ACK
        # This is normal part of this routine; each of these commands should fail
        try:
            part_write = i2c_msg.write(dev_addr, [pre_cmd])
            pprint(part_write)
            #read = i2c_msg.read(dev_addr, 1)
            bus.i2c_rdwr(part_write) #, read)
            # If somehow we got no exception, raise one
            raise ConnectionError("FW version acquire tripped as it expected NACK on a command")
        except Exception as ex:
            print("error {} ocured: {} ".format(ex.errno, ex.strerror))
            if ex.errno not in (121, 110, 5): # I/O error - usually means no ACK - this is what we expect
                raise

    # Now ManufacturerData() will contain FW version data which we can read; wait to make sure it's ready
    sleep(0.35) # EV2300 software waits 350 ms; but documentation doesn't explicitly say to wait here
    data = smbus_read_block(bus, dev_addr, 0x2f)
    print('ManufacturerData:', ' '.join(['{:02x}'.format(i) for i in data]))

data = smbus_read_block(bus, dev_addr, 0x20)
print('Manufacturer:', ' '.join(['{:02x}'.format(i) for i in data]))

sbs_read_firmware_version_bq_sealed(bus, dev_addr)

bus.close()
