# dryrun interface

from pmbusorgcli.interfaces import smbus_interface
from pmbusorgcli.byte_helpers import byte_transmission_str
from pmbusorgcli.pec import pec
from pmbusorgcli.smbus_helpers import writify_address, readify_address

dryrun_preamble = 'Dry run interface: '


class SMBusInterface(smbus_interface.SMBusInterfaceProtocol):

    def open(self):
        """Initialization method called before
        doing any transactions."""
        print(dryrun_preamble + 'initialize.')

    def send_byte(self,
                  address_byte,
                  data_byte,
                  is_using_pec):

        address_wr = writify_address(address_byte)

        if(is_using_pec):
            pec_byte = bytes([pec(address_wr + data_byte)])
            pec_str = byte_transmission_str(pec_byte)
        else:
            pec_str = ''

        print(dryrun_preamble +
              'send_byte' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(data_byte) +
              pec_str)

    def write_byte(self,
                   address_byte,
                   command_bytes,
                   data_byte,
                   is_using_pec):

        address_wr = writify_address(address_byte)

        if(is_using_pec):
            pec_byte = bytes([pec(address_wr + command_bytes + data_byte)])
            pec_str = byte_transmission_str(pec_byte)
        else:
            pec_str = ''

        print(dryrun_preamble +
              'write_byte' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(data_byte) +
              pec_str)

    def write_word(self,
                   address_byte,
                   command_bytes,
                   data_bytes,
                   is_using_pec):

        address_wr = writify_address(address_byte)

        if(is_using_pec):
            pec_byte = bytes([pec(address_wr + command_bytes + data_bytes)])
            pec_str = byte_transmission_str(pec_byte)
        else:
            pec_str = ''

        print(dryrun_preamble +
              'write_word' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(data_bytes) +
              pec_str)

    def write_block(self,
                    address_byte,
                    command_bytes,
                    data_bytes,
                    is_using_pec):

        address_wr = writify_address(address_byte)
        size_byte = bytes([len(data_bytes)])

        if(is_using_pec):
            pec_byte = bytes([pec(address_wr + command_bytes + data_bytes)])
            pec_str = byte_transmission_str(pec_byte)
        else:
            pec_str = ''

        print(dryrun_preamble +
              'write_block' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(size_byte) +
              byte_transmission_str(data_bytes) +
              pec_str)

    def receive_byte(self,
                     address_byte,
                     is_using_pec):

        address_rd = readify_address(address_byte)

        if(is_using_pec):
            pec_str = '[pec]'
        else:
            pec_str = ''

        print(dryrun_preamble +
              'receive_byte' +
              byte_transmission_str(address_rd) +
              '[rxdata]' +
              pec_str)

        return bytes([0])

    def read_byte(self,
                  address_byte,
                  command_bytes,
                  is_using_pec):

        address_wr = writify_address(address_byte)
        address_rd = readify_address(address_byte)

        if(is_using_pec):
            pec_str = '[pec]'
        else:
            pec_str = ''

        print(dryrun_preamble +
              'read_byte : ' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(address_rd) +
              '[rxdata]' +
              pec_str)

        return bytes([0])

    def read_word(self,
                  address_byte,
                  command_bytes,
                  is_using_pec):
        address_wr = writify_address(address_byte)
        address_rd = readify_address(address_byte)

        if(is_using_pec):
            pec_str = '[pec]'
        else:
            pec_str = ''

        print(dryrun_preamble +
              'read_byte : ' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(address_rd) +
              '[rxdata][rxdata]' +
              pec_str)

        return bytes([0, 1])

    def read_block(self,
                   address_byte,
                   command_bytes,
                   is_using_pec):
        address_wr = writify_address(address_byte)
        address_rd = readify_address(address_byte)

        if(is_using_pec):
            pec_str = '[pec]'
        else:
            pec_str = ''

        print(dryrun_preamble +
              'read_byte : ' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(address_rd) +
              '[size_byte][rxdata .... ]' +
              pec_str)

        return bytes([0, 1, 2, 3])

    def process_call(self,
                     address_byte,
                     command_bytes,
                     data_bytes,
                     is_using_pec):
        address_wr = writify_address(address_byte)
        address_rd = readify_address(address_byte)

        if(is_using_pec):
            pec_str = '[pec]'
        else:
            pec_str = ''

        print(dryrun_preamble +
              'process_call : ' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(data_bytes) +
              byte_transmission_str(address_rd) +
              '[rxdata][rxdata]' +
              pec_str)

        return bytes([0, 1])

    def block_process_call(self,
                           address_byte,
                           command_bytes,
                           data_bytes,
                           is_using_pec):
        address_wr = writify_address(address_byte)
        address_rd = readify_address(address_byte)

        size_byte = bytes([len(data_bytes)])

        if(is_using_pec):
            pec_str = '[pec]'
        else:
            pec_str = ''

        print(dryrun_preamble +
              'process_call : ' +
              byte_transmission_str(address_wr) +
              byte_transmission_str(command_bytes) +
              byte_transmission_str(size_byte) +
              byte_transmission_str(data_bytes) +
              byte_transmission_str(address_rd) +
              '[rxdata][rxdata]' +
              pec_str)

        return bytes([0, 1, 2, 3])


    def close(self):
        """Closing / destructor method after
         finished performing transactions."""

        print(dryrun_preamble + 'close.')
