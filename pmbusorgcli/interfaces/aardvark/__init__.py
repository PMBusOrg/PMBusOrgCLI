# aardvark interface

from pmbusorgcli.interfaces import smbus_interface
from pmbusorgcli.pec import pec
from pmbusorgcli.smbus_helpers import writify_address, readify_address

from aardvark_py import *


aardvark_i2c_status_strings = {
    0: 'AA_I2C_STATUS_OK',
    1: 'AA_I2C_STATUS_BUS_ERROR',
    2: 'AA_I2C_STATUS_SLA_ACK',
    3: 'AA_I2C_STATUS_SLA_NACK',
    4: 'AA_I2C_STATUS_DATA_NACK',
    5: 'AA_I2C_STATUS_ARB_LOST',
    6: 'AA_I2C_STATUS_BUS_LOCKED',
    7: 'AA_I2C_STATUS_LAST_DATA_ACK'
}


class SMBusInterface(smbus_interface.SMBusInterfaceProtocol):

    def open(self):
        """Initialization method called before
        doing any transactions."""

        aa_found_devices = aa_find_devices(1)
        assert aa_found_devices[0] != 0

        self.handle = aa_open(0)
        assert self.handle is not None

        bus_freq_in_khz = 100
        assert aa_i2c_bitrate(self.handle, bus_freq_in_khz) ==\
            bus_freq_in_khz

        # bus_timeout_in_ms = 25
        # assert aa_i2c_bus_timeout(self.handle, bus_timeout_in_ms) ==\
        #     bus_timeout_in_ms

    def send_byte(self,
                  address_byte,
                  data_byte,
                  is_using_pec):

        if(is_using_pec):
            pecout = bytes([pec(writify_address(address_byte) +
                                data_byte)])
            writeout = array('B', data_byte + pecout)
        else:
            writeout = array('B', data_byte)

        result = aa_i2c_write_ext(self.handle,
                                  address_byte[0],
                                  AA_I2C_NO_FLAGS,
                                  writeout)

        status = result[0]
        num_written = result[1]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(writeout)

    def write_byte(self,
                   address_byte,
                   command_bytes,
                   data_byte,
                   is_using_pec):

        if(is_using_pec):
            pecout = bytes([pec(writify_address(address_byte) +
                                command_bytes +
                                data_byte)])
            writeout = array('B', command_bytes +
                             data_byte +
                             pecout)
        else:
            writeout = array('B', command_bytes +
                             data_byte)

        result = aa_i2c_write_ext(self.handle,
                                  address_byte[0],
                                  AA_I2C_NO_FLAGS,
                                  writeout)

        status = result[0]
        num_written = result[1]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(writeout)

    def write_word(self,
                   address_byte,
                   command_bytes,
                   data_bytes,
                   is_using_pec):

        if(is_using_pec):
            pecout = bytes([pec(writify_address(address_byte) +
                                command_bytes +
                                data_bytes)])
            writeout = array('B', command_bytes +
                             data_bytes +
                             pecout)
        else:
            writeout = array('B', command_bytes +
                             data_bytes)

        result = aa_i2c_write_ext(self.handle,
                                  address_byte[0],
                                  AA_I2C_NO_FLAGS,
                                  writeout)

        status = result[0]
        num_written = result[1]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(writeout)

    def write_block(self,
                    address_byte,
                    command_bytes,
                    data_bytes,
                    is_using_pec):

        size_byte = bytes([len(data_bytes)])
        if(is_using_pec):
            pecout = bytes([pec(writify_address(address_byte) +
                         command_bytes +
                         size_byte +
                         data_bytes)])
            writeout = array('B', command_bytes +
                             size_byte +
                             data_byte +
                             pecout)
        else:
            writeout = array('B', command_bytes +
                             size_byte +
                             data_byte)

        result = aa_i2c_write_ext(self.handle,
                                  address_byte[0],
                                  AA_I2C_NO_FLAGS,
                                  writeout)

        status = result[0]
        num_written = result[1]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(writeout)

    def receive_byte(self,
                     address_byte,
                     is_using_pec):

        readlength = 1
        if is_using_pec:
            readlength += 1

        readback = array('B', [0] * readlength)
        result = aa_i2c_read_ext(self.handle,
                                 address_byte[0],
                                 AA_I2C_NO_FLAGS,
                                 readback)

        status = result[0]
        num_read = result[2]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        if not is_using_pec:
            readback_bytes = bytes(readback)
            return readback_bytes

        # if using pec
        readback_bytes = bytes(readback[0:-1])
        readback_pec = readback[-1]
        expected_pec = pec(readify_address(address_byte) +
                           readback_bytes)

        assert expected_pec == readback_pec
        return readback_bytes

    def read_byte(self,
                  address_byte,
                  command_bytes,
                  is_using_pec):

        readlength = 1
        if is_using_pec:
            readlength += 1

        readback = array('B', [0] * readlength)
        result = aa_i2c_write_read(self.handle,
                                   address_byte[0],
                                   AA_I2C_NO_FLAGS,
                                   array('B', command_bytes),
                                   readback)
        status = result[0]
        num_written = result[1]
        num_read = result[3]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(command_bytes)
        assert num_read == readlength

        if not is_using_pec:
            readback_bytes = bytes(readback)
            return readback_bytes

        # if using pec
        readback_bytes = bytes(readback[0:-1])
        readback_pec = readback[-1]
        expected_pec = pec(writify_address(address_byte) +
                           command_bytes +
                           readify_address(address_byte) +
                           readback_bytes)

        assert expected_pec == readback_pec
        return readback_bytes

    def read_word(self,
                  address_byte,
                  command_bytes,
                  is_using_pec):

        readlength = 2
        if is_using_pec:
            readlength += 1

        readback = array('B', [0] * readlength)
        result = aa_i2c_write_read(self.handle,
                                   address_byte[0],
                                   AA_I2C_NO_FLAGS,
                                   array('B', command_bytes),
                                   readback)
        status = result[0]
        num_written = result[1]
        num_read = result[3]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(command_bytes)
        assert num_read == readlength

        if not is_using_pec:
            readback_bytes = bytes(readback)
            return readback_bytes

        # if using pec
        readback_bytes = bytes(readback[0:-1])
        readback_pec = readback[-1]
        expected_pec = pec(writify_address(address_byte) +
                           command_bytes +
                           readify_address(address_byte) +
                           readback_bytes)

        assert expected_pec == readback_pec
        return readback_bytes

    def read_block(self,
                   address_byte,
                   command_bytes,
                   is_using_pec):

        if(is_using_PEC):
            # EXTRA1 flag means read extra byte
            # beyond returned size byte (for pec)
            flag = AA_I2C_SIZED_READ_EXTRA1
        else:
            flag = AA_I2C_SIZED_READ

        readbuffersize = 255
        readback = array('B', [0] * readbuffersize)
        result = aa_i2c_write_read(self.handle,
                                   address_byte[0],
                                   flag,
                                   array('B', command_bytes),
                                   readback)
        status = result[0]
        num_written = result[1]
        # num_read = result[3]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == len(command_bytes)
        readback_size = readback[0]
        readback_bytes = bytes(readback[1:readback_size])

        if not is_using_pec:
            return readback_bytes

        # if using pec
        readback_pec = readback[readback_size + 1]
        expected_pec = pec(writify_address(address_byte) +
                           command_bytes +
                           readify_address(address_byte) +
                           bytes([readback_size]) +
                           readback_bytes)

        assert expected_pec == readback_pec
        return readback_bytes

    def process_call(self,
                     address_byte,
                     command_bytes,
                     data_bytes,
                     is_using_pec):
        readlength = 2
        if is_using_pec:
            readlength += 1

        readback = array('B', [0] * readlength)
        result = aa_i2c_write_read(self.handle,
                                   address_byte[0],
                                   AA_I2C_NO_FLAGS,
                                   array('B', command_bytes +
                                         data_bytes),
                                   readback)
        status = result[0]
        num_written = result[1]
        num_read = result[3]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == (len(command_bytes) + len(data_bytes))
        assert num_read == readlength

        if not is_using_pec:
            readback_bytes = bytes(readback)
            return readback_bytes

        # if using pec
        readback_bytes = bytes(readback[0:-1])
        readback_pec = readback[-1]
        expected_pec = pec(writify_address(address_byte) +
                           command_bytes +
                           data_bytes +
                           readify_address(address_byte) +
                           readback_bytes)

        assert expected_pec == readback_pec
        return readback_bytes

    def block_process_call(self,
                           address_byte,
                           command_bytes,
                           data_bytes,
                           is_using_pec):

        if(is_using_PEC):
            # EXTRA1 flag means read extra byte
            # beyond returned size byte (for pec)
            flag = AA_I2C_SIZED_READ_EXTRA1
        else:
            flag = AA_I2C_SIZED_READ

        readbuffersize = 255
        readback = array('B', [0] * readbuffersize)
        result = aa_i2c_write_read(self.handle,
                                   address_byte[0],
                                   flag,
                                   array('B', command_bytes +
                                         data_bytes),
                                   readback)
        status = result[0]
        num_written = result[1]
        # num_read = result[3]

        if(status != AA_OK):
            raise RuntimeError('Transaction returned with error status: ' +
                               aardvark_i2c_status_strings[status])

        assert num_written == (len(command_bytes) + len(data_bytes))
        readback_size = readback[0]
        readback_bytes = bytes(readback[1:readback_size])

        if not is_using_pec:
            return readback_bytes

        # if using pec
        readback_pec = readback[readback_size + 1]
        expected_pec = pec(writify_address(address_byte) +
                           command_bytes +
                           data_bytes +
                           readify_address(address_byte) +
                           bytes([readback_size]) +
                           readback_bytes)

        assert expected_pec == readback_pec
        return readback_bytes

    def close(self):
        """Closing / destructor method after
         finished performing transactions."""
        aa_close(self.handle)
