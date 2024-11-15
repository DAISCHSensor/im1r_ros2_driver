#!/usr/bin/env python3

import struct
import math

# Define constants
HEAD = b'\xA5\x5A'
TAIL = b'\x0D\x0A'
HEAD_LEN = 2
DOM_LEN = 1
CMD_LEN = 1
LEN_LEN = 1
CRC_LEN = 1
TAIL_LEN = 2
USED_FRAME_LEN = 64


def checksum_crc(data, crc_ref):
    """
    :param data: Data to check
    :param crc_ref: Expected CRC value
    :return: True if checksum is correct, otherwise False
    """
    if len(crc_ref) == CRC_LEN: 
        crc = 0x00  # Initial value
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if (crc & 0x80) != 0:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc <<= 1
                crc &= 0xFF
        # Compare the calculated CRC with the reference CRC
        return crc == crc_ref[0]
    else:
        return False


# Parse frame data function
def parse_frame(frame):

    if len(frame) == USED_FRAME_LEN:
        head = frame[0:HEAD_LEN]
        dom = frame[HEAD_LEN:HEAD_LEN + DOM_LEN]
        cmd = frame[HEAD_LEN + DOM_LEN:HEAD_LEN + DOM_LEN + CMD_LEN]
        length = frame[HEAD_LEN + DOM_LEN + CMD_LEN:HEAD_LEN + DOM_LEN + CMD_LEN + LEN_LEN]

        cmd_value = struct.unpack('B', cmd)[0]
        Data_Len = struct.unpack('B', length)[0]

        data = frame[HEAD_LEN + DOM_LEN + CMD_LEN + LEN_LEN:HEAD_LEN + DOM_LEN + CMD_LEN + LEN_LEN + Data_Len]
        crc = frame[HEAD_LEN + DOM_LEN + CMD_LEN + LEN_LEN + Data_Len:
                    HEAD_LEN + DOM_LEN + CMD_LEN + LEN_LEN + Data_Len + CRC_LEN]

        if cmd_value == 1 and len(data) == Data_Len and checksum_crc(head + dom + cmd + length + data, crc):
            parsed_data = {
                'Count': struct.unpack('B', data[0:1])[0],
                'Timestamp': struct.unpack('<Q', data[1:9])[0],
                'AccX': struct.unpack('<f', data[9:13])[0],
                'AccY': struct.unpack('<f', data[13:17])[0],
                'AccZ': struct.unpack('<f', data[17:21])[0],
                'GyroX': struct.unpack('<f', data[21:25])[0],
                'GyroY': struct.unpack('<f', data[25:29])[0],
                'GyroZ': struct.unpack('<f', data[29:33])[0],
                'Pitch': struct.unpack('<f', data[33:37])[0],
                'Roll': struct.unpack('<f', data[37:41])[0],
                'Temperature': struct.unpack('<h', data[41:43])[0] * 0.1,
                'IMUStatus': struct.unpack('B', data[43:44])[0],
                'GyroBiasX': struct.unpack('<h', data[44:46])[0] * 0.0001,
                'GyroBiasY': struct.unpack('<h', data[46:48])[0] * 0.0001,
                'GyroBiasZ': struct.unpack('<h', data[48:50])[0] * 0.0001,
                'GyroStaticBiasX': struct.unpack('<h', data[50:52])[0] * 0.0001,
                'GyroStaticBiasY': struct.unpack('<h', data[52:54])[0] * 0.0001,
                'GyroStaticBiasZ': struct.unpack('<h', data[54:56])[0] * 0.0001
            }
            return parsed_data
        else:
            return None
    else:
        return None

    
def euler_to_quaternion(roll, pitch):
    roll = math.radians(roll)
    pitch = math.radians(pitch)
    qw = math.cos(roll / 2) * math.cos(pitch / 2)
    qx = math.sin(roll / 2) * math.cos(pitch / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2)
    qz = -math.sin(roll / 2) * math.sin(pitch / 2)
    return (qw, qx, qy, qz)