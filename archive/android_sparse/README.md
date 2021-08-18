<!--
SPDX-FileCopyrightText: 2021 Armijn Hemel <armijn+github@tjaldur.nl>

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
