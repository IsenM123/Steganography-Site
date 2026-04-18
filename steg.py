import struct

def bytes_to_bits(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits


def bits_to_bytes(bits):
    result = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | b
        result.append(byte)
    return bytes(result)


def embed(carrier_bytes, message_bytes, S, L):

    carrier = bytearray(carrier_bytes)

    # prepend message length (4 bytes)
    length_bytes = struct.pack("I", len(message_bytes))
    full_message = length_bytes + message_bytes

    message_bits = bytes_to_bits(full_message)

    bit_index = S
    msg_index = 0
    total_bits = len(carrier) * 8

    while msg_index < len(message_bits) and bit_index < total_bits:
        byte_pos = bit_index // 8
        bit_pos = 7 - (bit_index % 8)

        carrier[byte_pos] &= ~(1 << bit_pos)
        carrier[byte_pos] |= (message_bits[msg_index] << bit_pos)

        msg_index += 1
        bit_index += L
    print("Message bits:", len(message_bits))
    print("Available bits:", (len(carrier_bytes) * 8 - S) // L)
    if msg_index < len(message_bits):
        raise ValueError("Message too large for carrier with given S and L")
    

    return carrier


def extract(carrier_bytes, S, L):
    bits = []
    bit_index = S
    total_bits = len(carrier_bytes) * 8

    # First extract length (32 bits)
    while len(bits) < 32 and bit_index < total_bits:
        byte_pos = bit_index // 8
        bit_pos = 7 - (bit_index % 8)

        bit = (carrier_bytes[byte_pos] >> bit_pos) & 1
        bits.append(bit)

        bit_index += L

    length_bytes = bits_to_bytes(bits)
    message_length = struct.unpack("I", length_bytes)[0]

    # Now extract actual message
    bits = []
    while len(bits) < message_length * 8 and bit_index < total_bits:
        byte_pos = bit_index // 8
        bit_pos = 7 - (bit_index % 8)

        bit = (carrier_bytes[byte_pos] >> bit_pos) & 1
        bits.append(bit)

        bit_index += L

    return bits_to_bytes(bits)