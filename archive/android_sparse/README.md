<!--
SPDX-FileCopyrightText: 2021 Armijn Hemel <armijn+github@tjaldur.nl>
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## fill-4k-zeros.img

An Android sparse image that expands to a 4 KiB raw image filled with zero bytes.

It was created using the following commands:

    $ dd if=/dev/zero of=fill-4k-zeros.raw bs=4K count=1
    $ img2simg fill-4k-zeros.raw fill-4k-zeros.img

It can be converted back to a raw image with the following command:

    $ simg2img fill-4k-zeros.img fill-4k-zeros.raw

`img2simg` and `simg2img` are included in the package called

* `android-sdk-libsparse-utils` ([Debian](https://packages.debian.org/sid/android-sdk-libsparse-utils), [Ubuntu](https://packages.ubuntu.com/focal/android-sdk-libsparse-utils)) or
* `android-tools` ([Fedora](https://src.fedoraproject.org/rpms/android-tools), [openSUSE](https://build.opensuse.org/package/show/openSUSE%3AFactory/android-tools), [Arch Linux](https://archlinux.org/packages/community/x86_64/android-tools/)).

Source: own work

## extended-headers.img

A sparse image with all 4 types of chunks: `RAW`, `FILL`, `DONT_CARE`
and `CRC32`. The file header and chunk headers are extended by 4 bytes - instead
of the ~~28-byte~~ file header and ~~12-byte~~ chunk headers (which are the
standard sizes for version 1.0), file header is 32 bytes and chunk headers are
16 bytes in size.

These extended headers are not artificial - they appear in the wild.
See `oem_au_base.img` from [this page](
  https://docs.cubepilot.org/user-guides/herelink/herelink-user-guides/oem-image-setup#steps
)
(that is also the file used as an inspiration in creating this sample).

The file is tested on the reference implementation [`libsparse`](
  https://android.googlesource.com/platform/system/core/+/e8d02c50d7/libsparse
) from AOSP (actually, I cloned the GitHub repo
https://github.com/anestisb/android-simg2img which makes building somewhat
easier) - parsing doesn't reveal any errors and even the CRC check succeeds
(see [./extended-headers.py](./extended-headers.py) to find out how to enable it).

Python script for generating: [./extended-headers.py](./extended-headers.py)
