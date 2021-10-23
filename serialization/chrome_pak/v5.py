# SPDX-FileCopyrightText: 2012 The Chromium Authors
#
# SPDX-License-Identifier: BSD-3-Clause

# https://chromium.googlesource.com/chromium/src/tools/grit/+/8a23eae/grit/format/data_pack_unittest.py#42
data = (
    b'\x05\x00\x00\x00'                  # version
    b'\x01\x00\x00\x00'                  # encoding & padding
    b'\x03\x00'                          # resource_count
    b'\x01\x00'                          # alias_count
    b'\x01\x00\x28\x00\x00\x00'          # index entry 1
    b'\x04\x00\x28\x00\x00\x00'          # index entry 4
    b'\x06\x00\x34\x00\x00\x00'          # index entry 6
    b'\x00\x00\x40\x00\x00\x00'          # extra entry for the size of last
    b'\x0a\x00\x01\x00'                  # alias table
    b'this is id 4this is id 6')         # data

with open('v5.pak', 'wb') as f:
    f.write(data)
