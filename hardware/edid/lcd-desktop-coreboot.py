# SPDX-FileCopyrightText: 1994-2006 Video Electronics Standards Association
# SPDX-FileCopyrightText: 2020 Jakub Czapiga <jacz@semihalf.com>
# SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>
#
# SPDX-License-Identifier: GPL-2.0-only

# See
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

EDID_COLOR_R_X = 0x25 # Red X 0.640
EDID_COLOR_R_Y = 0x152 # Red Y 0.330
EDID_COLOR_G_X = 0x13a # Green X 0.300
EDID_COLOR_G_Y = 0x267 # Green Y 0.600
EDID_COLOR_B_X = 0x9a # Blue X 0.150
EDID_COLOR_B_Y = 0x3e # Blue Y 0.060
EDID_COLOR_W_X = 0xa # White X 0.3125
EDID_COLOR_W_Y = 0x22a # White Y 0.3291

data = (
    b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' +  # signature

    # Display product identification
    b'\x55\xcb' +  # manufacturer_id (manufacturer_name = EDID_MANUFACTURER_NAME = "UNK")
    uint16(0x1234) +  # product_code
    uint32(0x56789ABC) +  # serial_number
    uint8(0) +  # manufacture_week [= not specified]
    uint8(2015 - 1990) +  # manufacture_year

    # EDID version information
    uint8(1)  + # edid_version
    uint8(4)  + # edid_revision

    # Basic display parameters
    uint8(  # video_input_type
        0 << 7 |  # EDID_ANALOG_VSI
        0 << 5 |  # EDID_SIGNAL_LEVEL_0
        0 << 4 |  # EDID_VIDEO_SETUP_BLANK_EQ_BLACK
        1 << 3 |  # EDID_SEPARATE_SYNC_H_AND_V(v)
        1 << 2 |  # EDID_COMPOSITE_SYNC_H(v)
        1 << 1 |  # EDID_COMPOSITE_SYNC_ON_GREEN(v)
        1 << 0    # EDID_SERRATION_VSYNC(v)
    ) +
    uint8(43) +  # horizontal_size [cm]
    uint8(32) +  # vertical_size [cm]
    uint8(120) +  # display_gamma [= 220%]
    uint8(  # supported_features
        0 << 7 |  # EDID_STANDBY_MODE(v)
        0 << 6 |  # EDID_SUSPEND_MODE(v)
        1 << 5 |  # EDID_ACTIVE_OFF(v)
        0 << 3 |  # EDID_COLOR_FORMAT_RGB444
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
    uint8(1 << 6 | ((85 - 60) & 0x1f)) +  # [1] = 4:3, 85 Hz

    uint8((1600 // 8 - 31) & 0xFF) +  # [2] = 1600px
    uint8(1 << 6 | ((75 - 60) & 0x1f)) +  # [3] = 4:3, 75 Hz

    uint8((1600 // 8 - 31) & 0xFF) +  # [4] = 1600px
    uint8(1 << 6 | ((70 - 60) & 0x1f)) +  # [5] = 4:3, 70 Hz

    uint8((1600 // 8 - 31) & 0xFF) +  # [6] = 1600px
    uint8(1 << 6 | ((65 - 60) & 0x1f)) +  # [7] = 4:3, 65 Hz

    uint8((1280 // 8 - 31) & 0xFF) +  # [8] = 1280px
    uint8(2 << 6 | ((85 - 60) & 0x1f)) +  # [9] = 5:4, 85 Hz

    uint8((1280 // 8 - 31) & 0xFF) +  # [10] = 1280px
    uint8(2 << 6 | ((60 - 60) & 0x1f)) +  # [11] = 5:4, 60 Hz

    uint8((1024 // 8 - 31) & 0xFF) +  # [12] = 1024px
    uint8(1 << 6 | ((85 - 60) & 0x1f)) +  # [13] = 4:3, 85 Hz

    uint8((800 // 8 - 31) & 0xFF) +  # [14] = 800px
    uint8(1 << 6 | ((85 - 60) & 0x1f)) +  # [15] = 4:3, 85 Hz

    # descriptor_block_1[18]
    uint16((162000000 // 10000) & 0xFFFF) +  # [0:1] = EDID_PIXEL_CLOCK(v)

    # Horizontal Addressable Video is 1600px
    # Horizontal Blanking is 560px
    uint8(0x40) +  # [2]
    uint8(0x30) +  # [3]
    uint8(0x62) +  # [4]

    # Vertical Addressable Video is 1200 lines
    # Vertical Blanking is 50 lines
    uint8(0xB0) +  # [5]
    uint8(0x32) +  # [6]
    uint8(0x40) +  # [7]

    uint8(64) +  # [8] = Horizontal Front Porch [px]
    uint8(192) +  # [9] = Horizontal Pulse Sync Width [px]
    uint8(0x13) +  # [10] = Vertical Front Porch is 1 line
    uint8(0x00) +  # [11] = Vertical Sync Pulse Width is 3 lines

    # Horizontal Addressable Image Size is 427 mm
    # Vertical Addressable Image Size is 320 mm
    uint8(0xAB) +  # [12]
    uint8(0x40) +  # [13]
    uint8(0x13) +  # [14]

    uint8(0) +  # [15] = Horizontal Border Size is 0 px
    uint8(0) +  # [16] = Vertical Border Size is 0 lines

    # Timing is Non-Interlaced Video,
    # Stereo Video is not supported,
    # Digital Separate Syncs are required.
    uint8(0x1E) +  # [17]

    # descriptor_block_2[18]
    # Display Range Limits Block Tag
    b'\x00\x00\x00\xFD' +  # [0:3]

    uint8(0) +  # [4] = Horizontal and Vertical Rate Offsets are zero
    uint8(50) +  # [5] = Minimum Vertical Freq is 50 Hz
    uint8(90) +  # [6] = Maximum Vertical Freq is 90 Hz

    uint8(30) +  # [7] = Minimum Horizontal Freq is 30 kHz
    uint8(110) +  # [8] = Maximum Horizontal Freq is 110 kHz
    uint8(23) +  # [9] = Maximum Pixel Clock Freq is 230 MHz
    uint8(0x4) +  # [10] = Begin CVT Support Info
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
    uint8(0x7F) +  # [6] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L177-L185
    uint8(0x0F) +  # [7] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L188-L193
    uint8(0x03) +  # [8] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L196-L199
    uint8(0x87) +  # [9] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L202-L207
    uint8(0xC0) +  # [10] = https://github.com/ElyesH/coreboot/blob/e0af9fcb2d/tests/lib/edid-test.c#L210-L213
    uint8(0x0) +  # [11] = 1920 timings are not supported

    b'\x00' * 6 +  # [12:17]

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

with open('lcd-desktop-coreboot.bin', 'wb') as f:
    f.write(data)
