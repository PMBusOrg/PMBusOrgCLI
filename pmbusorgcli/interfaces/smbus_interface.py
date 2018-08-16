
class SMBusInterfaceProtocol:
    "Protocol that smbus interfaces will need to comply with."

    def name(self):
        """Name for the interface"""
        cls = self.__class__
        return '{}.{}'.format(cls.__module__, cls.__name__)

    def open(self):
        """Initialization method called before
        doing any transactions."""

    def send_byte(self,
                  address_byte,
                  data_byte,
                  is_using_pec):
        """
        Send byte transaction

        Inputs:
        data_byte - single byte to be sent
        is_using_pec - boolean to use pec or not

        Returns:

        """

    def write_byte(self,
                   address_byte,
                   command_bytes,
                   data_byte,
                   is_using_pec):
        """
        Write byte transaction

        Inputs:
        command_bytes - bytes for command/extended command
        data_byte - single byte to be written
        is_using_pec - boolean to use pec or not

        Returns:

        """

    def write_word(self,
                   address_byte,
                   command_bytes,
                   data_bytes,
                   is_using_pec):
        """
        Write byte transaction

        Inputs:
        command_bytes - bytes for command/extended command
        data_bytes - bytes to be written,
        is_using_pec - boolean to use pec or not

        Returns:

        """

    def write_block(self,
                    address_byte,
                    command_bytes,
                    data_bytes,
                    is_using_pec):
        """
        Write block transaction

        Inputs:
        command_bytes - bytes for command/extended command
        data_bytes - bytes to be written,
        is_using_pec - boolean to use pec or not

        Returns:
        """

    def receive_byte(self,
                     address_byte,
                     is_using_pec):
        """
        Receive Byte

        Inputs:
        is_using_pec - boolean to use pec or not

        Returns:
        data byte
        """

    def read_byte(self,
                  address_byte,
                  command_bytes,
                  is_using_pec):
        """
        Read Byte

        Inputs:
        command_bytes
        is_using_pec - boolean to use pec or not

        Returns:
        data byte
        """

    def read_word(self,
                  address_byte,
                  command_bytes,
                  is_using_pec):
        """
        Read Word

        Inputs:
        command_bytes
        is_using_pec - boolean to use pec or not

        Returns:
        data bytes
        """

    def read_block(self,
                   address_byte,
                   command_bytes,
                   is_using_pec):
        """
        Read Block

        Inputs:
        command_bytes
        is_using_pec - boolean to use pec or not

        Returns:
        data bytes (size byte excluded)
        """

    def process_call(self,
                     address_byte,
                     command_bytes,
                     data_bytes,
                     is_using_pec):
        """
        Inputs:
        command_bytes
        data_bytes
        is_using_pec - boolean to use pec or not

        Returns:
        data bytes
        """

    def block_process_call(self,
                           address_byte,
                           command_bytes,
                           data_bytes,
                           is_using_pec):
        """
        Inputs:
        command_bytes
        data_bytes
        is_using_pec - boolean to use pec or not

        Returns:
        data bytes (size byte excluded)
        """

    def close(self):
        """Closing / destructor method after
         finished performing transactions."""
