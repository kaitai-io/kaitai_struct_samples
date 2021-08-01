# SPDX-FileCopyrightText: 1994-2006 Video Electronics Standards Association
# SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>
#
# SPDX-License-Identifier: CC0-1.0

# See
#   - https://glenwing.github.io/docs/VESA-EEDID-A2.pdf - Section 6.1 (example 1)
#   - https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L45-L256
#   - https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/include/lib/edid-test.h

# Code structure inspired by https://github.com/mathiasbynens/small/pull/50#issue-49006046

import struct

endian = 'little'

def uint8(number):
    return number.to_bytes(1, byteorder = endian)

def uint16(number):
    return number.to_bytes(2, byteorder = endian)

def uint32(number):
    return number.to_bytes(4, byteorder = endian)

def get_raw_edid_checksum(x):
    assert len(x) == 127, 'Unexpected length of checksum input: expected {}, but got {}'.format(127, len(x))

    sum = 0
    for i in range(127):
        sum += x[i]

    return -sum & 0xFF

# chroma_coords = [0.627, 0.341, 0.292, 0.605, 0.149, 0.072, 0.283, 0.297]
# print('\n'.join([hex(round(c * 1024.0)) for c in chroma_coords]))

EDID_COLOR_R_X = 0x282  # Red X is 0.627
EDID_COLOR_R_Y = 0x15d  # Red Y is 0.341
EDID_COLOR_G_X = 0x12b  # Green X is 0.292
EDID_COLOR_G_Y = 0x26c  # Green Y is 0.605
EDID_COLOR_B_X = 0x99  # Blue X is 0.149
EDID_COLOR_B_Y = 0x4a  # Blue Y is 0.072
EDID_COLOR_W_X = 0x122  # White X is 0.283
EDID_COLOR_W_Y = 0x130  # White Y is 0.297

data = (
    b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' +  # signature

    # Display product identification
    b'\x04\x43' +  # manufacturer_id (manufacturer_name = "ABC")
    uint16(0xF206) +  # product_code
    uint32(0x00000001) +  # serial_number
    uint8(1) +  # manufacture_week [= 1st week]
    uint8(2007 - 1990) +  # manufacture_year

    # EDID version information
    uint8(1)  + # edid_version
    uint8(4)  + # edid_revision

    # Basic display parameters
    uint8(  # video_input_type
        0 << 7 |  # EDID_ANALOG_VSI
        0b00 << 5 |  # EDID_SIGNAL_LEVEL_0
        0 << 4 |  # EDID_VIDEO_SETUP_BLANK_EQ_BLACK
        1 << 3 |  # EDID_SEPARATE_SYNC_H_AND_V(v)
        1 << 2 |  # EDID_COMPOSITE_SYNC_H(v)
        1 << 1 |  # EDID_COMPOSITE_SYNC_ON_GREEN(v)
        1 << 0    # EDID_SERRATION_VSYNC(v)
    ) +
    uint8(43) +  # horizontal_size [cm]
    uint8(32) +  # vertical_size [cm]
    uint8(round(2.2 * 100) - 100) +  # display_gamma [= 2.2]
    uint8(  # supported_features
        0 << 7 |  # EDID_STANDBY_MODE(v)
        0 << 6 |  # EDID_SUSPEND_MODE(v)
        1 << 5 |  # EDID_ACTIVE_OFF(v)
        0b01 << 3 |  # EDID_COLOR_TYPE_RGB
        0 << 2 |  # EDID_SRGB_SUPPORTED(v)
        1 << 1 |  # EDID_PREFERRED_TIMING_EXTENDED_INFO
        1 << 0    # EDID_DISPLAY_FREQUENCY_CONTINUOUS
    ) +

    # Color space definition
    # color_characteristics[10]
    uint8(  # [0] = EDID_COLOR_RG_XY
        ((((EDID_COLOR_R_X & 0x3) << 2) | (EDID_COLOR_R_Y & 0x3)) << 4) |  # (EDID_COLOR_R_X10_Y10 << 4)
        (((EDID_COLOR_G_X & 0x3) << 2) | (EDID_COLOR_G_Y & 0x3))  # EDID_COLOR_G_X10_Y10
    ) +
    uint8(  # [1] = EDID_COLOR_BW_XY
        ((((EDID_COLOR_B_X & 0x3) << 2) | (EDID_COLOR_B_Y & 0x3)) << 4) |  # (EDID_COLOR_B_X10_Y10 << 4)
        (((EDID_COLOR_W_X & 0x3) << 2) | (EDID_COLOR_W_Y & 0x3))  # EDID_COLOR_W_X10_Y10
    ) +
    uint8(EDID_COLOR_R_X >> 2) +  # [2] = EDID_COLOR_R_X92
    uint8(EDID_COLOR_R_Y >> 2) +  # [3] = EDID_COLOR_R_Y92
    uint8(EDID_COLOR_G_X >> 2) +  # [4] = EDID_COLOR_G_X92
    uint8(EDID_COLOR_G_Y >> 2) +  # [5] = EDID_COLOR_G_Y92
    uint8(EDID_COLOR_B_X >> 2) +  # [6] = EDID_COLOR_B_X92
    uint8(EDID_COLOR_B_Y >> 2) +  # [7] = EDID_COLOR_B_Y92
    uint8(EDID_COLOR_W_X >> 2) +  # [8] = EDID_COLOR_W_X92
    uint8(EDID_COLOR_W_Y >> 2) +  # [9] = EDID_COLOR_W_Y92

    # Timing information
    # established_supported_timings[2]
    uint8(  # [0]
        1 << 7 |  # EDID_ESTABLISHED_TIMINGS_1_720x400_70Hz
        1 << 6 |  # EDID_ESTABLISHED_TIMINGS_1_720x400_88Hz
        1 << 5 |  # EDID_ESTABLISHED_TIMINGS_1_640x480_60Hz
        1 << 4 |  # EDID_ESTABLISHED_TIMINGS_1_640x480_67Hz
        1 << 3 |  # EDID_ESTABLISHED_TIMINGS_1_640x480_72Hz
        1 << 2 |  # EDID_ESTABLISHED_TIMINGS_1_640x480_75Hz
        1 << 1 |  # EDID_ESTABLISHED_TIMINGS_1_800x600_56Hz
        1 << 0   # EDID_ESTABLISHED_TIMINGS_1_800x600_60Hz
    ) +
    uint8(  # [1]
        1 << 7 |  # EDID_ESTABLISHED_TIMINGS_2_800x600_72Hz
        1 << 6 |  # EDID_ESTABLISHED_TIMINGS_2_800x600_75Hz
        1 << 5 |  # EDID_ESTABLISHED_TIMINGS_2_832x624_75Hz
        1 << 4 |  # EDID_ESTABLISHED_TIMINGS_2_1024x768_80HzI
        1 << 3 |  # EDID_ESTABLISHED_TIMINGS_2_1024x768_60Hz
        1 << 2 |  # EDID_ESTABLISHED_TIMINGS_2_1024x768_70Hz
        1 << 1 |  # EDID_ESTABLISHED_TIMINGS_2_1024x768_75Hz
        1 << 0    # EDID_ESTABLISHED_TIMINGS_2_1280x1024_75Hz
    ) +
    uint8(1 << 7) +  # manufacturers_reserved_timing
    # standard_timings_supported[16]
    uint8((1600 // 8 - 31) & 0xFF) +  # [0] = 1600px
    uint8(1 << 6 | ((85 - 60) & 0x1F)) +  # [1] = 4:3, 85 Hz

    uint8((1600 // 8 - 31) & 0xFF) +  # [2] = 1600px
    uint8(1 << 6 | ((75 - 60) & 0x1F)) +  # [3] = 4:3, 75 Hz

    uint8((1600 // 8 - 31) & 0xFF) +  # [4] = 1600px
    uint8(1 << 6 | ((70 - 60) & 0x1F)) +  # [5] = 4:3, 70 Hz

    uint8((1600 // 8 - 31) & 0xFF) +  # [6] = 1600px
    uint8(1 << 6 | ((65 - 60) & 0x1F)) +  # [7] = 4:3, 65 Hz

    uint8((1280 // 8 - 31) & 0xFF) +  # [8] = 1280px
    uint8(2 << 6 | ((85 - 60) & 0x1F)) +  # [9] = 5:4, 85 Hz

    uint8((1280 // 8 - 31) & 0xFF) +  # [10] = 1280px
    uint8(2 << 6 | ((60 - 60) & 0x1F)) +  # [11] = 5:4, 60 Hz

    uint8((1024 // 8 - 31) & 0xFF) +  # [12] = 1024px
    uint8(1 << 6 | ((85 - 60) & 0x1F)) +  # [13] = 4:3, 85 Hz

    uint8((800 // 8 - 31) & 0xFF) +  # [14] = 800px
    uint8(1 << 6 | ((85 - 60) & 0x1F)) +  # [15] = 4:3, 85 Hz

    # descriptor_block_1[18]
    uint16((162000000 // 10000) & 0xFFFF) +  # [0:1] = EDID_PIXEL_CLOCK(v)

    # Horizontal Addressable Video is 1600px
    # Horizontal Blanking is 560px
    uint8(1600 & 0xFF) +  # [2]
    uint8(560 & 0xFF) +  # [3]
    uint8(  # [4]
        (1600 & 0xF00) >> 4 |
        (560 & 0xF00) >> 8
    ) +

    # Vertical Addressable Video is 1200 lines
    # Vertical Blanking is 50 lines
    uint8(1200 & 0xFF) +  # [5]
    uint8(50 & 0xFF) +  # [6]
    uint8(  # [7]
        (1200 & 0xF00) >> 4 |
        (50 & 0xF00) >> 8
    ) +

    # Horizontal Front Porch is 64px
    # Horizontal Sync Pulse Width is 192px
    # Vertical Front Porch is 1 line
    # Vertical Sync Pulse Width is 3 lines
    uint8(64 & 0xFF) +  # [8]
    uint8(192 & 0xFF) +  # [9]
    uint8(  # [10]
        (1 & 0xF) << 4 |
        (3 & 0xF) << 0
    ) +
    uint8(  # [11]
        (64 & 0x300) << 6 |
        (192 & 0x300) << 4 |
        (1 & 0x30) << 2 |
        (3 & 0x30) << 0
    ) +

    # Horizontal Addressable Image Size is 427 mm
    # Vertical Addressable Image Size is 320 mm
    uint8(427 & 0xFF) +  # [12]
    uint8(320 & 0xFF) +  # [13]
    uint8(  # [14]
        (427 & 0xF00) >> 4 |
        (320 & 0xF00) >> 8
    ) +

    uint8(0) +  # [15] = Horizontal Border Size is 0 px
    uint8(0) +  # [16] = Vertical Border Size is 0 lines

    # Timing is Non-Interlaced Video,
    # Stereo Video is not supported,
    # Digital Separate Syncs are required.
    uint8(0x1E) +  # [17]

    # descriptor_block_2[18]
    # Display Range Limits Block Tag
    b'\x00\x00\x00\xFD' +  # [0:3]

    uint8(0x00) +  # [4] = Horizontal and Vertical Rate Offsets are zero
    uint8(50) +  # [5] = Minimum Vertical Freq is 50 Hz
    uint8(90) +  # [6] = Maximum Vertical Freq is 90 Hz

    uint8(30) +  # [7] = Minimum Horizontal Freq is 30 kHz
    uint8(110) +  # [8] = Maximum Horizontal Freq is 110 kHz
    uint8(23) +  # [9] = Maximum Pixel Clock Freq is 230 MHz
    b'\x04' +  # [10] = Begin CVT Support Info
    uint8(0x11) +  # [11] = Compatible with CVT Version 1.1
    uint8(0) +  # [12] = Maximum Pixel Clock Freq remains at 230 MHz
    uint8(200) +  # [13] = Maximum Active Pixels per Line is 1600
    uint8(0x90) +  # [14] = Supported aspect ratios: 4:3, 5:4

    uint8(0) +  # [15] = Preferred Aspect Ratio is 4:3, Standard CVT Blanking is supported
    uint8(0x50) +  # [16] = H. & V. Stretch are supported, H. & V. Shrink are not supported
    uint8(60) +  # [17] = Preferred Refresh Rate is 60 Hz

    # descriptor_block_3[18]
    # Established Timings III Block Tag
    b'\x00\x00\x00\xF7\x00' +  # [0:4]

    uint8(10) +  # [5] = VESA DMT Standard Version #10
    uint8(  # [6] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L177-L185 (warning: wrong value 0x7F in the `coreboot` code, should be 0xF7)
        1 << 7 |  # 640x350@85Hz
        1 << 6 |  # 640x400@85Hz
        1 << 5 |  # 720x400@85Hz
        1 << 4 |  # 640x480@85Hz
        0 << 3 |  # 848x480@60Hz
        1 << 2 |  # 800x600@85Hz
        1 << 1 |  # 1024x768@85Hz
        1 << 0    # 1152x864@75Hz
    ) +
    uint8(  # [7] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L188-L193
        0 << 7 |  # 1280x768@60Hz (RB)    Note: (RB) means reduced blanking
        0 << 6 |  # 1280x768@60Hz
        0 << 5 |  # 1280x768@75Hz
        0 << 4 |  # 1280x768@85Hz
        1 << 3 |  # 1280x960@60Hz
        1 << 2 |  # 1280x960@85Hz
        1 << 1 |  # 1280x1024@60Hz
        1 << 0    # 1280x1024@85Hz
    ) +
    uint8(  # [8] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L196-L199
        0 << 7 |  # 1360x768@60Hz
        0 << 6 |  # 1440x900@60Hz (RB)
        0 << 5 |  # 1440x900@60Hz
        0 << 4 |  # 1440x900@75Hz
        0 << 3 |  # 1440x900@85Hz
        0 << 2 |  # 1400x1050@60Hz (RB)
        1 << 1 |  # 1400x1050@60Hz
        1 << 0    # 1400x1050@75Hz
    ) +
    uint8(  # [9] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L202-L207
        1 << 7 |  # 1400x1050@85Hz
        0 << 6 |  # 1680x1050@60Hz (RB)
        0 << 5 |  # 1680x1050@60Hz
        0 << 4 |  # 1680x1050@75Hz
        0 << 3 |  # 1680x1050@85Hz
        1 << 2 |  # 1600x1200@60Hz
        1 << 1 |  # 1600x1200@65Hz
        1 << 0    # 1600x1200@70Hz
    ) +
    uint8(  # [10] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L210-L213
        1 << 7 |  # 1600x1200@75Hz
        1 << 6 |  # 1600x1200@85Hz
        0 << 5 |  # 1792x1344@60Hz
        0 << 4 |  # 1792x1344@75Hz
        0 << 3 |  # 1856x1392@60Hz
        0 << 2 |  # 1856x1392@75Hz
        0 << 1 |  # 1920x1200@60Hz (RB)
        0 << 0    # 1920x1200@60Hz
    ) +
    uint8(  # [11] = 1920 timings are not supported
        0 << 7 |  # 1920x1200@75Hz
        0 << 6 |  # 1920x1200@85Hz
        0 << 5 |  # 1920x1440@60Hz
        0 << 4 |  # 1920x1440@75Hz
        0b0000 << 0  # Reserved Bits: Shall be set to '0000'.
    ) +

    b'\x00' * 6 +  # [12:17] = Reserved Bytes

    # descriptor_block_4[18]
    # Display Product Name Block Tag
    b'\x00\x00\x00\xFC\x00' +  # [0:4]
    b'ABC LCD21\n' + b' ' * 3 +  # [5:17]

    # Number of optional 128-byte extension blocks
    uint8(0)  # extension_flag [= no extensions]
)

data += (
    uint8(get_raw_edid_checksum(data))  # checksum
)

with open('vesa-edid-1.4-example1.bin', 'wb') as f:
    f.write(data)
