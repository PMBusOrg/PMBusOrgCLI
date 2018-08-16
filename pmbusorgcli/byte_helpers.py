
def byte_transmission_str(bytes):
    transstr = ''
    for byte in bytes:
        transstr += '[' + format(byte, '02X') + ']'
    return transstr

def hexstr_to_bytes(input):
    assert len(input) % 2 == 0

    if(input[0:2] == '0x'):
        input = input[2:]

    # input_byte_indexes = list(range(0, len(input), 2))
    # byte_string_array = list(map(
    #     lambda x: input[x:(x + 2)], input_byte_indexes))

    # bytes = list(map(lambda x: int(x, 16), byte_string_array))
    # return bytes

    b = bytes.fromhex(input)
    return b
