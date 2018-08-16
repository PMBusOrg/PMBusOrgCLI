# pec.py
# methods to perform a crc-8 calcuation on a
# series of bytes for use in
# smbus packet error checking packets.
#

# The CRC polynomial of
# x^8 + x^2 + x^1 + 1 is in
# the most significant 9 bits.
crc_poly = 0x8380

# CRC is done after the polynomial
# shifts one byte.
crc_done = 0x0083


def pec_processbyte(current_crc, input_byte):
    # initialize polynomial before it starts shifting
    poly_temp = crc_poly
    # testMask is used to evaluate whether we should XOR
    test_mask = 0x8000

    # XOR previous CRC and current input for multi-byte CRC
    # calculations. The temporary result, crcTemp, is shifted
    # left one byte to perform direct mode calculation
    crc_temp = (current_crc ^ input_byte) << 8

    while poly_temp != crc_done:
        if crc_temp & test_mask:
            crc_temp = crc_temp ^ poly_temp
        test_mask = test_mask >> 1
        poly_temp = poly_temp >> 1

    return crc_temp & 0xFF


def pec(bytes):
    current_crc = 0

    for byte in bytes:
        current_crc = pec_processbyte(current_crc, byte)

    return current_crc
