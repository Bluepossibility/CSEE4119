import json

MAX_PAYLOAD = 576
OUTPUT_FILE = "output.txt"


def checksum(data):
    """
    calculate the internet check sum: 16-bit
    """
    #data = str(data)
    s = 0
    if len(data) % 2 == 1:
        data = data + "\0"  # padding
    # loop taking 2 characters at a time
    for i in range(0, len(data), 2):
        w = ord(data[i]) + (ord(data[i + 1]) << 8)
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 16)
    # complement and mask to 4 byte short
    s = ~s & 0xffff
    return s


def not_corrupted(TCP_header, data, is_from_sender):
    """
    :param TCP_header:
    :param data:
    :return: True of False indicating whether checksum of data match checksum.
    """
    try:
        header_checksum = TCP_header[-2]

    except KeyError as e:
        print("KeyError occurs: ", str(e))
        return False
    except Exception as e:
        print("Unknown Error: ", str(e))
        return False

    if checksum(data) == header_checksum:
        return True
    else:
        print('checksum(data): ', checksum(data))
        print('header_checksum: ', header_checksum)
        print("Checksum does not match data, the packet is corrupted!")
        return False
