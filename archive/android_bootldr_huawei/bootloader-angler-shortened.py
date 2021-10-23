# SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>
#
# SPDX-License-Identifier: CC0-1.0

# See
#   - https://android.googlesource.com/device/huawei/angler/+/673cfb9/releasetools.py
#   - https://source.codeaurora.org/quic/la/device/qcom/common/tree/meta_image/meta_format.h?h=LA.UM.6.1.1&id=a68d284aee85
#   - https://androidfilehost.com/?fid=24407100847292744 "bootloader-angler-angler-01.31.img"

# Code structure inspired by https://github.com/mathiasbynens/small/pull/50#issue-49006046

endian = 'little'

def uint8(number):
    return number.to_bytes(1, byteorder = endian)

def uint16(number):
    return number.to_bytes(2, byteorder = endian)

def uint32(number):
    return number.to_bytes(4, byteorder = endian)

def pad_to_4(s, p):
    return s + p * (-len(s) % 4)

MAX_IMAGES = 16

meta_header_sizeof = 76  # [= sizeof(meta_header) = 4 + 2 + 2 + 64 + 2 + 2]
img_header_entry_sizeof = 80  # [= 72 + 4 + 4]
img_header_entries_sizeof = MAX_IMAGES * img_header_entry_sizeof

data = (
    # meta_header
    uint32(0xce1ad63c) +  # magic
    uint16(1) +  # major_version
    uint16(0) +  # minor_version
    b'angler-01.31'.ljust(64, b'\x00') +  # img_version
    uint16(meta_header_sizeof) +  # meta_hdr_size
    uint16(img_header_entries_sizeof)  # img_hdr_size
)

assert len(data) == meta_header_sizeof, (
    'Unexpected sizeof(meta_header): wrote {} in the `meta_header`, but I am currently at {}'
    .format(meta_header_sizeof, len(data))
)

partitions = [
    {  # img_header[0]
        'name': b'partition',
        'body': pad_to_4(b'GPT with protective MBR', b'\x00'),
    },
    {  # img_header[1]
        'name': b'sbl1',
        # http://vm1.duckdns.org/Public/Qualcomm-Secure-Boot/Qualcomm-Secure-Boot.htm
        'body': pad_to_4(b'Secondary Boot Loader 1', b'\x00'),
    },
    {  # img_header[2]
        'name': b'tz',
        # https://bits-please.blogspot.com/2015/08/exploring-qualcomms-trustzone.html
        'body': pad_to_4(b'TrustZone image', b'\x00'),
    },
    {  # img_header[3]
        'name': b'rpm',
        # https://forum.xda-developers.com/t/info-android-device-partitions-and-filesystems.3586565/#post-71782262
        'body': pad_to_4(b'Resource Power Manager', b'\x00'),
    },
    {  # img_header[4]
        'name': b'sdi',
        'body': pad_to_4(b'Secure Disk Image', b'\x00'),
    },
    {  # img_header[5]
        'name': b'pmic',
        # https://www.facebook.com/boxdongleactivation.global/posts/340216493123357
        'body': pad_to_4(b'Power Management Integrated Circuit', b'\x00'),
    },
    {  # img_header[6]
        'name': b'hyp',
        'body': pad_to_4(b'Hypervisor', b'\x00'),
    },
    {  # img_header[7]
        'name': b'cmnlib',
        'body': pad_to_4(b'Common library for trusted apps', b'\x00'),
    },
    {  # img_header[8]
        'name': b'keymaster',
        'body': pad_to_4(b'KeyMaster module', b'\x00'),
    },
    {  # img_header[9]
        'name': b'aboot',
        # https://www.quora.com/Which-Android-file-is-altered-when-unlocking-a-bootloader
        # https://android.stackexchange.com/a/73131
        # https://alephsecurity.com/2017/05/23/nexus6-initroot/#secure-boot-in-nexus-6
        'body': pad_to_4(b'Applications Bootloader', b'\x00'),
    },
]

start_offset = meta_header_sizeof + img_header_entries_sizeof

for p in partitions:
    len_body = len(p['body'])
    # p['start_offset'] = start_offset - 1 if p['name'] == b'sbl1' else start_offset  # p['start_offset'] assertion test
    p['start_offset'] = start_offset
    data += (
        p['name'].ljust(72, b'\x00') +  # ptn_name
        uint32(start_offset) +  # start_offset
        uint32(len_body)  # size
    )
    start_offset += len_body

data += (
    # img_header[10:15] (MAX_IMAGES = 16)
    (b'\x00' * (72 + 4 + 4)) * (MAX_IMAGES - len(partitions))
)

for i, p in enumerate(partitions):
    pos = len(data)
    assert pos == p['start_offset'], (
        'Unexpected start_offset for partitions[{}]: wrote {} in the `img_header` entry, but I am currently at {}'
        .format(i, p['start_offset'], pos)
    )
    data += p['body']

with open('bootloader-angler-shortened.img', 'wb') as f:
    f.write(data)
