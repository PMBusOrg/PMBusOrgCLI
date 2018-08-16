
smbus_transaction_write_types = ['send_byte',
                                 'write_byte',
                                 'write_word',
                                 'write_block',
                                 ]

smbus_transaction_read_types = ['receive_byte',
                                'read_byte',
                                'read_word',
                                'read_block',
                                ]

smbus_transaction_process_call_types = ['process_call',
                                        'block_read_block_write_process_call']

smbus_transaction_types = smbus_transaction_read_types +\
    smbus_transaction_write_types +\
    smbus_transaction_process_call_types


def writify_address(address_byte_unshifted):
    assert len(address_byte_unshifted) == 1
    return bytes([address_byte_unshifted[0] << 1])


def readify_address(address_byte_unshifted):
    assert len(address_byte_unshifted) == 1
    return bytes([(address_byte_unshifted[0] << 1) + 1])
