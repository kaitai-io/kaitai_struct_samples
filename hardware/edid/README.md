<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

A very large repository of EDIDs from real monitors, both digital and analog: https://github.com/linuxhw/EDID

## edid-1.0.bin

Example of the old EDID 1.0 version.

Source: https://git.linuxtv.org/edid-decode.git/tree/test/edid-1.0.test?id=9ca8433

## edid-1.1.bin

Example of the old EDID 1.1 version.

Source: https://git.linuxtv.org/edid-decode.git/tree/test/edid-1.1.test?id=9ca8433

## edid-1.2.bin

Example of the old EDID 1.2 version.

Source: https://git.linuxtv.org/edid-decode.git/tree/test/edid-1.2.test?id=9ca8433

## vesa-edid-1.4-example1.py

Sample base EDID (block 0) data structure for a typical LCD Desktop Display from the [VESA E-EDID Standard Release A2 (EDID 1.4)](https://glenwing.github.io/docs/VESA-EEDID-A2.pdf) (Section 6.1).

Source: https://git.linuxtv.org/edid-decode.git/tree/test/vesa-edid-1.4-1.test?id=9ca8433

Python script for generating (run `python3 vesa-edid-1.4-example1.py` to regen): [./vesa-edid-1.4-example1.py](./vesa-edid-1.4-example1.py)

> Note: the example directly in the EDID 1.4 standard has incorrect value of _Checksum_ at the very end, probably due to human error (there is ~~`0x0b`~~, should be <ins>`0x9a`</ins>). The [_vesa-edid-1.4-1.test_ file](https://git.linuxtv.org/edid-decode.git/tree/test/vesa-edid-1.4-1.test?id=9ca8433) from the `edid-decode` repository has this error fixed.
