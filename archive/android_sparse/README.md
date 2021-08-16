<!--
SPDX-FileCopyrightText: 2021 Armijn Hemel <armijn+github@tjaldur.nl>

SPDX-License-Identifier: CC0-1.0
-->

## android_sparse.img

An Android sparse image, that expands to a 4 KiB raw image filled with zero bytes.

It was created using the following commands:

    $ dd if=/dev/zero of=android_sparse.raw bs=4K count=1
    $ img2simg android_sparse.raw android_sparse.img

It can be converted back to a raw image with the following command:

    $ simg2img android_sparse.img android_sparse.raw

`img2simg` and `simg2img` are part of the `android_tools` package.

Source: own work
