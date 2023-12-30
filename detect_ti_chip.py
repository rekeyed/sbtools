#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
from time import sleep

bus = SMBus(1)
dev_addr = 0x0b

known_chips = {
    0x0450 : 'BQ20z45',
    0x0453 : 'BQ20x453',
    0x0500 : 'BQ30z50',
    0x0550 : 'BQ30z55',
    0x0554 : 'BQ30z554',
    0x0650 : 'BQ20z65',
    0x3050 : 'BQ3050',
    0x3060 : 'BQ3060',
    0x4307 : 'BQ40z307',
    0x9db2 : 'BQ40370',
    0x0100 : 'BQ35100',
    0x0110 : 'BQ34110',
    0x0210 : 'BQ34210',
    0x0220 : 'BQ27220',
    0x0320 : 'BQ27320',
    0x0421 : 'BQ27421',
    0x0425 : 'BQ27425',
    0x0426 : 'BQ27426',
    0x0510 : 'BQ27510',
    0x0520 : 'BQ27520',
    0x0530 : 'BQ27530',
    0x0531 : 'BQ27531',
    0x0532 : 'BQ27532',
    0x0541 : 'BQ27541',
    0x0542 : 'BQ27542',
    0x0545 : 'BQ27545',
    0x0546 : 'BQ27546',
    0x0621 : 'BQ27621',
    0x0742 : 'BQ27742',
    0x1100 : 'BQ78z100',
    0x1561 : 'BQ27z561',
    0x1e9b : 'BQ78350',
    0x2610 : 'BQ28z610',
    0x4500 : 'BQ40z50',
    0x4600 : 'BQ40z60',
    0x4800 : 'BQ40z80',
    0x9e34 : 'BQ4050',
    0x7692 : 'BQ769x2'
}

def sbs_read_firmware_version_bq_sealed(bus, dev_addr):
    """ Reads firmware version from BQ series chips

    got it here:
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
            part_write = i2c_msg.write(dev_addr, [pre_cmd, 0x3e])
            print("Raw write: ", " ".join("{:02x}".format(i) for i in bytes(part_write)))
            bus.i2c_rdwr(part_write)
            # If somehow we got no exception, raise one
            raise ConnectionError("FW version acquire tripped as it expected NACK on a command")
        except Exception as ex:
            print("error {} ocured: {} (it's OK, don't worry)".format(ex.errno, ex.strerror))
            if ex.errno not in (121, 110, 5): # I/O error - usually means no ACK - this is what we expect
                raise

    # Now ManufacturerData() will contain FW version data which we can read; wait to make sure it's ready
    sleep(0.35) # EV2300 software waits 350 ms; but documentation doesn't explicitly say to wait here
    write = i2c_msg.write(dev_addr, [0x2f])
    read = i2c_msg.read(dev_addr, 18)
    bus.i2c_rdwr(write, read)
    return list(read)

tries = 3
while (tries > 0):
    data = sbs_read_firmware_version_bq_sealed(bus, dev_addr)
    print('Raw data:', ' '.join(['{:02x}'.format(i) for i in data]))
    if (data[0] < 10 or data[0] > 15):
        print('Answer size is wrong, retry({})...'.format(tries));
        tries -= 1
    else:
        data = data[1:data[0] + 1]
        tries = -1
if (tries == 0):
    print('Chip detection failded: wrong answer received :(')
else:
    chip_id = data[0] << 8 | data[1]
    if (chip_id in known_chips.keys()):
        print('Detected chip:', known_chips[chip_id])
    else:
        print('Chip is unknown, chip ID: 0x{:04x}'.format(chip_id))


bus.close()
