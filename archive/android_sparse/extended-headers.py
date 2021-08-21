# SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>
#
# SPDX-License-Identifier: CC0-1.0

# See
#   - https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/sparse_format.h
#   - https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/output_file.cpp
#   - https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/sparse_read.cpp

# Code structure inspired by https://github.com/mathiasbynens/small/pull/50#issue-49006046

import binascii

endian = 'little'

def uint8(number):
    return number.to_bytes(1, byteorder = endian)

def uint16(number):
    return number.to_bytes(2, byteorder = endian)

def uint32(number):
    return number.to_bytes(4, byteorder = endian)

data = (
    # sparse_header
    uint32(0xed26ff3a) +  # magic
    uint16(1) +  # major_version
    uint16(0) +  # minor_version
    uint16(32) +  # file_hdr_sz
    uint16(16) +  # chunk_hdr_sz
    uint32(0x400) +  # blk_sz
    uint32(6) +  # total_blks
    uint32(4) +  # total_chunks
    uint32(0) +  # image_checksum
    b'\x00' * 4 +

    # chunks[0]
    #   chunk_header
    uint16(0xCAC1) +  # chunk_type [= CHUNK_TYPE_RAW]
    uint16(0) +  # reserved1
    uint32(1) +  # chunk_sz
    uint32(16 + 0x400) +  # total_sz
    b'\x00' * 4 +
    #   body
    bytes([x & 0xff for x in range(0x400)]) +

    # chunks[1]
    #   chunk_header
    uint16(0xCAC2) +  # chunk_type [= CHUNK_TYPE_FILL]
    uint16(0) +  # reserved1
    uint32(2) +  # chunk_sz
    uint32(16 + 4) +  # total_sz
    b'\x00' * 4 +
    #   body
    b'ABC\x00' +

    # chunks[2]
    #   chunk_header
    uint16(0xCAC3) +  # chunk_type [= CHUNK_TYPE_DONT_CARE]
    uint16(0) +  # reserved1
    uint32(3) +  # chunk_sz
    uint32(16 + 0) +  # total_sz
    b'\x00' * 4 +
    #   body (none)

    # chunks[3]
    #   chunk_header
    uint16(0xCAC4) +  # chunk_type [= CHUNK_TYPE_CRC32]
    uint16(0) +  # reserved1
    uint32(0) +  # chunk_sz
    uint32(16 + 4) +  # total_sz
    b'\x00' * 4
    #   body
    # ... CRC32 checksum
)

checksum = 0
checksum = binascii.crc32(bytes([x & 0xff for x in range(0x400)]), checksum)  # chunks[0]

# Note: the CRC-32 checksum generation (which is disabled by default, but can be
# enabled by editing the source code - search for `out->use_crc`) in
# <https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/output_file.cpp>
# contains 2 bugs:
#
#   * For `FILL` chunks, the `chunk_sz` is disregarded and only one filled block
#     is included in the checksum (i.e. as if `chunk_sz` was always set to `1`):
#     <https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/output_file.cpp#364>
#
#   * `DONT_CARE` chunks are not included in the CRC-32 at all:
#     <https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/output_file.cpp#336>
#
# If you want to verify that the CRC-32 checksum is correct, rather enable CRC
# checking in `sparse_read.cpp` (which does not contain these errors) by passing
# `true` to the parameter `bool crc` of function `sparse_file_read_sparse`
# (you have to modify the code) - see
# <https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse/sparse_read.cpp#336>.

filler_repeat_count = (2 * 0x400) // 4
checksum = binascii.crc32(b'ABC\x00' * filler_repeat_count, checksum)  # chunks[1]

checksum = binascii.crc32(b'\x00' * (3 * 0x400), checksum)  # chunks[2]

data += (
    uint32(checksum & 0xFFFF_FFFF)
)

with open('extended-headers.img', 'wb') as f:
    f.write(data)
