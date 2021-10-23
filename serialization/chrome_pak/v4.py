# SPDX-FileCopyrightText: 2012 The Chromium Authors
#
# SPDX-License-Identifier: BSD-3-Clause

# https://chromium.googlesource.com/chromium/src/tools/grit/+/8a23eae/grit/format/data_pack_unittest.py#21
data = (
    b'\x04\x00\x00\x00'                  # header(version
    b'\x04\x00\x00\x00'                  #        no. entries,
    b'\x01'                              #        encoding)
    b'\x01\x00\x27\x00\x00\x00'          # index entry 1
    b'\x04\x00\x27\x00\x00\x00'          # index entry 4
    b'\x06\x00\x33\x00\x00\x00'          # index entry 6
    b'\x0a\x00\x3f\x00\x00\x00'          # index entry 10
    b'\x00\x00\x3f\x00\x00\x00'          # extra entry for the size of last
    b'this is id 4this is id 6')         # data

with open('v4.pak', 'wb') as f:
    f.write(data)
